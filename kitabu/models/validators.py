#-*- coding=utf-8 -*-

from importlib import import_module
from datetime import datetime

from django.db import models

from kitabu.exceptions import InvalidPeriod, TooManyReservations
from kitabu import managers

import time

# using datetime.now in this way allows to mock it with mock.patch and test nicely
now = datetime.now
SECONDS_IN_DAY = 3600 * 24
HOURS_IN_WEEK = 7 * 24


class Validator(models.Model):
    class Meta:
        app_label = 'kitabu'

    actual_validator_related_name = models.CharField(max_length=200, editable=False)

    apply_to_all = models.BooleanField(default=False)

    objects = models.Manager()
    universal = managers.Universal()

    def __unicode__(self):
        return getattr(self, self.actual_validator_related_name).__class__.__name__ + ' ' + unicode(self.id)

    def validate(self, reservation):
        # TODO: think whether this is not a good idea
        # assert reservation.id is None, "Reservation must be validated before being saved to database"
        getattr(self, self.actual_validator_related_name)._perform_validation(reservation)

    def save(self, *args, **kwargs):
        '''
        This method sets up actual validators related name accordingly to child class
        calling save.

        It is not meant for calling directly on this parent class intances. If you
        really need to save instance of this class pass keyword argument force=True
        '''
        if self.__class__ is Validator and not kwargs.get('force'):
            raise TypeError("Cannot save instance of Validator. Save only children classes instances")
        if not self.actual_validator_related_name:
            self.actual_validator_related_name = self.__class__.__name__.lower()
        return super(Validator, self).save(*args, **kwargs)

    def _perform_validation(self, reservation):
        ''' Method meant to be overridden. This one actually runs validations. '''
        raise NotImplementedError('Must be implemented in subclasses!')


class FullTimeValidator(Validator):
    class Meta:
        abstract = True

    TIME_UNITS = ['microsecond', 'second', 'minute', 'hour', 'day']

    interval = models.PositiveSmallIntegerField()
    interval_type = models.CharField(max_length=6, choices=[(x, x) for x in TIME_UNITS[1:]])

    def _perform_validation(self, reservation):
        date_field_names = self._get_date_field_names()
        dates = [getattr(reservation, field_name) for field_name in date_field_names]
        assert all([isinstance(date, datetime) for date in dates])

        for date in dates:
            for time_unit in self.TIME_UNITS:
                time_value = getattr(date, time_unit)

                if self.interval_type == time_unit:
                    if self.interval == 0 and time_value > 0:
                        raise InvalidPeriod(
                            "%ss must be 0 (%s is not)" % (time_unit, time_value),
                            reservation,
                            self)
                    if self.interval > 0 and time_value % self.interval > 0:
                        raise InvalidPeriod(
                            "%ss must by divisible by %s (%s is not)" % (time_unit, self.interval, time_value),
                            reservation,
                            self)
                    break  # don't validate any greater time units than this one
                elif time_value > 0:
                    raise InvalidPeriod(
                        "%ss must by 0 (got %s)" % (time_unit, time_value),
                        reservation,
                        self)

    def _get_date_field_names(self):
        return ['start', 'end']


class StaticValidator(Validator):
    class Meta:
        abstract = True

    validator_function_absolute_name = models.CharField(max_length=200, unique=True)

    def save(self, *args, **kwargs):
        if not kwargs.pop('force_validation_function_name', False):
            # raise AttributeError if validator_function_absolute_name cannot
            # be imported:
            self._get_validation_function()
        return super(StaticValidator, self).save(*args, **kwargs)

    def _perform_validation(self, reservation):
        self._get_validation_function()(reservation)

    def _get_validation_function(self):
        path = self.validator_function_absolute_name.split('.')
        base_module = import_module(path[0])

        return reduce(getattr, path[1:], base_module)


class TimeIntervalValidator(Validator):
    class Meta:
        abstract = True

    TIME_UNITS = ['second', 'minute', 'hour', 'day']
    NOT_LATER = 'l'
    NOT_SOONER = 's'
    INTERVAL_TYPES_CHOICES = [
        (NOT_LATER, 'maximum time span from now'),
        (NOT_SOONER, 'minimum time span from now'),
    ]

    time_value = models.PositiveSmallIntegerField(default=1)
    time_unit = models.CharField(max_length=6, choices=[(x, x) for x in TIME_UNITS], default='second')
    interval_type = models.CharField(max_length=2, choices=INTERVAL_TYPES_CHOICES, default=NOT_SOONER)

    def _perform_validation(self, reservation):
        date_field_names = self._get_date_field_names()
        dates = [getattr(reservation, field_name) for field_name in date_field_names]
        assert all([isinstance(date, datetime) for date in dates])

        for (date, field_name) in zip(dates, date_field_names):
            delta = date - now()

            valid = True

            if self.time_unit == 'second':
                valid = self._check(delta.total_seconds(), self.time_value)
            elif self.time_unit == 'minute':
                valid = self._check(delta.total_seconds(), self.time_value * 60)
            elif self.time_unit == 'hour':
                valid = self._check(delta.total_seconds(), self.time_value * 3600)
            elif self.time_unit == 'day':
                valid = self._check(delta.days, self.time_value)
            else:
                raise ValueError("time_unit must be one of (second, minute, hour, day)")

            if not valid:
                raise InvalidPeriod(
                    "Reservation %(field_name)s must by at %(least_most)s %(number)s %(time_unit)ss in the future" %
                    {
                        'field_name': field_name,
                        'least_most': 'least' if self.interval_type == self.NOT_SOONER else "most",
                        'number': self.time_value,
                        'time_unit': self.time_unit,
                    },
                    reservation,
                    self
                )

    def _get_date_field_names(self):
        return ['start', 'end']

    def _check(self, delta, expected_time):
        if self.interval_type == self.NOT_SOONER:
            return delta >= expected_time
        if self.interval_type == self.NOT_LATER:
            return delta <= expected_time


class WithinPeriodValidator(Validator):

    class Meta:
        abstract = True

    def _perform_validation(self, reservation):
        date_field_names = self._get_date_field_names()
        dates = [getattr(reservation, field_name) for field_name in date_field_names]
        assert all([isinstance(date, datetime) for date in dates])

        for period in self.periods.all():
            all_fields_valid_for_period = True
            for (date, field_name) in zip(dates, date_field_names):
                if (
                    (period.end and date > period.end)  # after end
                    or
                    (period.start and date < period.start)  # before start
                ):
                    all_fields_valid_for_period = False

            if all_fields_valid_for_period:
                return

        raise InvalidPeriod(
            "Reservation %s must be in one of given periods: %s, received: %s" %
            (
                field_name,
                ", ".join(map(unicode, self.periods.all())),
                date,
            ),
            reservation,
            self)

    def _get_date_field_names(self):
        return ['start', 'end']


class Period(models.Model):
    '''
    In this model implementation it is obligatory to implement foreign key
    pointing to WithinPeriodValidator model with related name of "periods", e.g.:

    validator = models.ForeignKey('WithinPeriodValidator', related_name='periods')
    '''

    class Meta:
        abstract = True

    start = models.DateTimeField(null=True, blank=True)
    end = models.DateTimeField(null=True, blank=True)

    def __unicode__(self):
        return "<%s, %s>" % (self.start, self.end)


class NotWithinPeriodValidator(Validator):
    '''
    This validator expects only reservations that have "start" and "end" fields.
    This way it can assure not only that all field are not in period, but also
    that reservation period does not cover whole validator period.
    '''
    class Meta:
        abstract = True

    start = models.DateTimeField()
    end = models.DateTimeField()

    def _perform_validation(self, reservation):
        assert self.start <= self.end

        date_field_names = ['start', 'end']
        dates = [getattr(reservation, field_name) for field_name in date_field_names]

        assert all([isinstance(date, datetime) for date in dates])

        for (date, field_name) in zip(dates, date_field_names):
            if self.start <= date <= self.end:
                raise InvalidPeriod(
                    "Reservation %s must not be between %s and %s" % (field_name, self.start, self.end),
                    reservation,
                    self)
            if reservation.start <= self.start <= self.end <= reservation.end:
                raise InvalidPeriod(
                    "Reservation cannot cover period between %s and %s" % (self.start, self.end),
                    reservation,
                    self)


class GivenHoursAndWeekdaysValidator(Validator):
    class Meta:
        abstract = True

    monday = models.PositiveIntegerField()
    tuesday = models.PositiveIntegerField()
    wednesday = models.PositiveIntegerField()
    thursday = models.PositiveIntegerField()
    friday = models.PositiveIntegerField()
    saturday = models.PositiveIntegerField()
    sunday = models.PositiveIntegerField()

    def _perform_validation(self, reservation):
        reservation_bitlist = self._get_hours_bitlist(reservation.start, reservation.end)

        list_and = self._list_and(self._to_hours_bitlist(), reservation_bitlist)

        if not list_and == map(lambda x: True if x else False, reservation_bitlist):
            raise InvalidPeriod("Reservation in wrong hours", reservation, self)

    def _get_hours_bitlist(self, start, end):
        start_timestamp = self._date_to_timestamp(start) / SECONDS_IN_DAY
        end_timestamp = self._date_to_timestamp(end) / SECONDS_IN_DAY
        days_delta = int(end_timestamp) - int(start_timestamp)

        if days_delta < 0:
            return [0] * HOURS_IN_WEEK
        elif days_delta > 7:
            return [1] * HOURS_IN_WEEK
        else:
            return self._hours_to_bitlist(self._hour_nr_in_week(start), self._hour_nr_in_week(end))

    def _date_to_timestamp(self, date):
        return time.mktime(date.timetuple())

    def _hours_to_bitlist(self, start_hour, end_hour):
        if start_hour <= end_hour:
            return [0] * start_hour + [1] * (end_hour - start_hour + 1) + [0] * (HOURS_IN_WEEK - end_hour - 1)
        else:
            return [1] * (end_hour + 1) + [0] * (start_hour - end_hour - 1) + [1] * (HOURS_IN_WEEK - start_hour)

    def _hour_nr_in_week(self, datetime):
        day = datetime.weekday()
        return day * 24 + datetime.hour

    def _list_and(self, *lists):
        return [all(tup) for tup in zip(*lists)]

    def _to_hours_bitlist(self):
        return reduce(lambda acc, day: acc + self._hours_number_to_bitlist(day), self._days(), [])

    def _hours_number_to_bitlist(self, number):
        bitlist = [1 if digit == '1' else 0 for digit in bin(number)[2:]]
        bitlist_length = len(bitlist)
        if bitlist_length < 24:
            bitlist = [0] * (24 - bitlist_length) + bitlist

        return bitlist

    def _days(self):
        return [self.monday, self.tuesday, self.wednesday, self.thursday, self.friday, self.saturday, self.sunday]

    @classmethod
    def create_from_bitlists(cls, bitlists_dict):
        def bitlist_to_int(bitlist):
            return reduce(lambda a, v: a * 2 + v, bitlist, 0)

        kwargs = {}
        for key, bitlist in bitlists_dict.items():
            kwargs[key] = bitlist_to_int(bitlist)

        return cls.objects.create(**kwargs)


class MaxDurationValidator(Validator):
    class Meta:
        abstract = True

    max_duration_in_seconds = models.PositiveIntegerField()

    def _perform_validation(self, reservation):
        date_field_names = ['start', 'end']
        dates = [getattr(reservation, field_name) for field_name in date_field_names]

        assert all([isinstance(date, datetime) for date in dates])
        delta = (reservation.end - reservation.start)
        duration = delta.days * 3600 * 24 + delta.seconds

        if duration > self.max_duration_in_seconds:
            raise InvalidPeriod('Max reservation duration exceeded', reservation, self)


class MaxReservationsPerUserValidator(Validator):
    '''
    Requires `Reservation` model to have field `owner`, which can be virtually anything,
    as long as it uniquely identifies a user. Likely it will be foreign key to `User` model.
    '''
    class Meta:
        abstract = True

    max_reservations_on_current_subject = models.PositiveSmallIntegerField(default=0, help_text="0 means no limit")
    max_reservations_on_all_subjects = models.PositiveSmallIntegerField(default=0, help_text="0 means no limit")

    def _perform_validation(self, reservation):
        if self.max_reservations_on_current_subject:
            reservations_so_far = reservation.subject.reservations.filter(
                end__gte=now(), owner=reservation.owner).count()
            if reservations_so_far >= self.max_reservations_on_current_subject:
                raise TooManyReservations(reservation, validator=self, current=True)
        if self.max_reservations_on_all_subjects:
            reservations_so_far = reservation.__class__.objects.filter(
                end__gte=now(), owner=reservation.owner).count()
            if reservations_so_far >= self.max_reservations_on_all_subjects:
                raise TooManyReservations(reservation, validator=self, current=False)
