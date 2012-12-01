#-*- coding=utf-8 -*-

from importlib import import_module
from datetime import datetime

from django.db import models

from kitabu.exceptions import ValidationError
from kitabu import managers

import time

# using datetime.now in this way allows to mock it with mock.patch and test nicely
now = datetime.now


class Validator(models.Model):
    class Meta:
        app_label = 'kitabu'

    actual_validator_related_name = models.CharField(max_length=200, editable=False)

    apply_to_all = models.BooleanField(default=False)

    objects = models.Manager()
    universal = managers.Universal()

    def validate(self, reservation):
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
                        raise ValidationError("%ss must be 0 (%s is not)" % (time_unit, time_value))
                    if self.interval > 0 and time_value % self.interval > 0:
                        raise ValidationError("%ss must by divisible by %s (%s is not)" %
                                              (time_unit, self.interval, time_value))
                    break  # don't validate any greater time units than this one
                elif time_value > 0:
                    raise ValidationError("%ss must by 0 (got %s)" %
                                          (time_unit, time_value))

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
                raise ValidationError(
                    "Reservation %(field_name)s must by at %(least_most)s %(number)s %(time_unit)ss in the future" %
                    {
                        'field_name': field_name,
                        'least_most': 'least' if self.interval_type == self.NOT_SOONER else "most",
                        'number': self.time_value,
                        'time_unit': self.time_unit,
                    }
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

    start = models.DateTimeField(null=True, blank=True)
    end = models.DateTimeField(null=True, blank=True)

    def _perform_validation(self, reservation):
        date_field_names = self._get_date_field_names()
        dates = [getattr(reservation, field_name) for field_name in date_field_names]
        assert all([isinstance(date, datetime) for date in dates])

        for (date, field_name) in zip(dates, date_field_names):
            if self.end and date > self.end:
                raise ValidationError("Reservation %s must not be later than %s" %
                                      (field_name, self.end))
            if self.start and date < self.start:
                raise ValidationError("Reservation %s must not be earlier than %s" %
                                      (field_name, self.start))

    def _get_date_field_names(self):
        return ['start', 'end']


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
                raise ValidationError("Reservation %s must not be between %s and %s" %
                                      (field_name, self.start, self.end))
            if reservation.start <= self.start <= self.end <= reservation.end:
                raise ValidationError("Reservation cannot cover period between %s and %s" %
                                      (self.start, self.end))


class GivenHoursAndWeekdaysValidator(Validator):
    class Meta:
        abstract = True

    days = models.PositiveIntegerField()  # 0 - 127
    hours = models.PositiveIntegerField()  # 0 - 16777215 (2 ** 24)

    def _perform_validation(self, reservation):
        assert 0 <= self.days <= 127
        assert 0 <= self.hours <= 16777215

        if not self._valid_hours(reservation):
            raise ValidationError("Reservation in wrong hours")
        if not self._valid_days(reservation):
            raise ValidationError("Reservation in wrong days")

    def _valid_hours(self, reservation):
        return self._valid_units(reservation=reservation, delta_method_name='_get_hours_delta',
                                 checking_property_name='hours')

    def _valid_days(self, reservation):
        return self._valid_units(reservation=reservation, delta_method_name='_get_days_delta',
                                 checking_property_name='days')

    def _valid_units(self, reservation, delta_method_name, checking_property_name):
        delta_method = getattr(self, delta_method_name)
        checking_property = getattr(self, checking_property_name)
        units_delta = delta_method(reservation.start, reservation.end)
        return (units_delta & checking_property) == units_delta

    def _get_days_delta(self, start, end):
        return self._get_delta(start=start, end=end, seconds_in_unit=3600 * 24, nr_units=7,
                               datetime_method_name='weekday')

    def _get_hours_delta(self, start, end):
        return self._get_delta(start=start, end=end, seconds_in_unit=3600, nr_units=24,
                               datetime_method_name='hour')

    def _get_delta(self, start, end, seconds_in_unit, nr_units, datetime_method_name):
        '''
            Return list of needed hours or days (e.g. [1,1,1,...,1,0,0,1]) converted to integer
        '''
        start_timestamp = self._date_to_timestamp(start) / seconds_in_unit
        end_timestamp = self._date_to_timestamp(end) / seconds_in_unit
        delta = int(end_timestamp) - int(start_timestamp)
        if delta < 0:
            return 0
        elif delta >= (nr_units - 1):
            return (2 ** nr_units) - 1
        else:
            current_representation = 0
            start_attr = getattr(start, datetime_method_name)
            end_attr = getattr(end, datetime_method_name)
            if callable(start_attr):
                (current_unit, end_unit) = (start_attr(), end_attr())
            else:
                (current_unit, end_unit) = (start_attr, end_attr)

            if end_unit < current_unit:
                end_unit += nr_units

            while current_unit <= end_unit:
                current_representation += 2 ** ((nr_units - 1) - (current_unit % nr_units))
                current_unit += 1
            return current_representation

    def _date_to_timestamp(self, date):
        return time.mktime(date.timetuple())

    @classmethod
    def create_from_bitlists(cls, hours, days):
        def bitlist_to_int(bitlist):
            return reduce(lambda a, v: a * 2 + v, bitlist, 0)

        return cls.objects.create(hours=bitlist_to_int(hours), days=bitlist_to_int(days))


class MaxDurationValidator(Validator):
    class Meta:
        abstract = True
