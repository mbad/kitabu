#-*- coding=utf-8 -*-

from importlib import import_module
from datetime import datetime, timedelta, time

from django.db import models

from kitabu.exceptions import (
    TimeUnitNotNull,
    TimeUnitNotDivisible,
    TooSoon,
    TooLate,
    OutsideAllowedPeriods,
    ForbiddenPeriod,
    ForbiddenHours,
    TooLong,
    TooManyReservationsForUser,
    TooManyReservationsOnSubjectForUser,
)
from kitabu import managers

# using datetime.now in this way allows to mock it with mock.patch and test nicely
now = datetime.now
SECONDS_IN_DAY = 3600 * 24
HOURS_IN_WEEK = 7 * 24


class Validator(models.Model):
    """Base class for all reservation validators.

    As opposed to most models in Kitabu this is not an abstract model. All
    validators inherit from it using django multi table inheritance. With this
    approach it is possible to have many-to-many relationship of Subject and
    Validator. The actual model that implements validation can be accessed
    from instance of the ``Validator`` via field named as content of
    actual_validator_related_name (see implementation of __unicode__).

    This class provides ``validate`` method that takes a fresh (not yet saved)
    reservation and checks whether it is ok to save, but provides no logic of
    validation. Validation logic must be implemented in subclasses in method
    ``_perform_validation``, that shell be called from the ``validate`` method.

    Methods:
        validate            - called to validate reservation, invodes _perform_validation
                              from subclass
        _perform_validation - actual validation logic. Must be overriden in
                              subclass

    Fields:
        actual_validator_related_name :: CharField
            - name of object property linking to subclass with implementation
        apply_to_all :: BooleanField
            - Flag to indicate whether this validator should be aplied to
            all reservations as opposed to applying to reservations on
            subjects defined by many-to-many relationship

    Subclassing
    -----------

    To subclass this Model simply inherit from it and implement
    ``_perform_validation`` method that takes reservation and possibly raises
    ``kitabu.exceptions.ReservationValidationError``. It may be desired to add custom
    subclasses of the ReservationValidationError to give better information on why
    reservation is not possible.

    """
    class Meta:
        app_label = 'kitabu'

    actual_validator_related_name = models.CharField(max_length=200, editable=False)

    apply_to_all = models.BooleanField(default=False)

    objects = models.Manager()
    universal = managers.Universal()

    def __unicode__(self):
        return getattr(self, self.actual_validator_related_name).__class__.__name__ + ' ' + unicode(self.id)

    def validate(self, reservation, allow_reservation_update=False):
        """Validate reservation and raise ReservationValidationError if not valid.

        This method accesses releated submodel instances and runs its
        ``_perform_validation``.

        Unless explicitely given ``allow_reservation_update`` argument that is
        True, forbids validation on already saved reservation. The reason for
        such behavior is not that validating saved reservation is error by
        itself, but most likely it will cause errors, because if reservation
        doesn't validate it probably should never make it to the database.

        """
        if not allow_reservation_update:
            assert reservation.id is None, "Reservation must be validated before being saved to database"
        getattr(self, self.actual_validator_related_name)._perform_validation(reservation)

    def get_forbidden_periods(self, start, end, size=1):
        """Get all unavailable periods between start and end."""
        return []

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
        ''' Method meant to be overridden. This one actually runs validation. '''
        raise NotImplementedError('Must be implemented in subclasses!')


class FullTimeValidator(Validator):
    """Validator for full time.

    Allows to ensure that start end end time will have only given precision.

    E.g. to allows only full and half hours, one would use ``interval type``
    of ``minute`` and interval of 30. If one wanted to allow only reservations
    for full days one would use ``interval_type`` of 'day' and ``interval`` of 1
    or 'hour' and 0 respectively.

    ``interval_type`` must be one of 'microsecond', 'second', 'minute', 'hour',
    'day'.

    ``interval`` is the most granular portion of ``interval_type`` that is
    allowed.

    """
    class Meta:
        abstract = True

    TIME_UNITS = ['microsecond', 'second', 'minute', 'hour', 'day']

    interval = models.PositiveSmallIntegerField()
    interval_type = models.CharField(max_length=6, choices=[(x, x) for x in TIME_UNITS[1:]])

    def _perform_validation(self, reservation):
        for date in [reservation.start, reservation.end]:
            for time_unit in self.TIME_UNITS:
                time_value = getattr(date, time_unit)

                if self.interval_type == time_unit:
                    if self.interval == 0 and time_value > 0:
                        raise TimeUnitNotNull(time_unit)
                    if self.interval > 0 and time_value % self.interval > 0:
                        raise TimeUnitNotDivisible(time_unit, self.interval)
                    break  # don't validate any greater time units than this one
                elif time_value > 0:
                    raise TimeUnitNotNull(time_unit)


class StaticValidator(Validator):
    """Validator that doesn't require any additional data.

    If a validation function doesn't need any variables that shell customize
    its behavior (i.e. database fields) then StaticValidator is the way to go.

    Possible usecases could be a forbidding validator that will always raise
    ReservationValidationError, to indicate that subject is not available or a validator
    that can calculate bank holidays.

    """
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
    """Validation for how far in the future reservation is.

    It has two possible functionalities: make sure reservation is far enough
    if the future or it is not too far.

    Possible usecases: one wants every customer to reserve a room at least
    a day, and not more than 3 months before the reservation is needed.

    Fields:
        interval_type: not sooner or not later than given period
        time_unit: days, hours, minutes, or seconds
        time_value: numerical value of the time_unit

    """
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
    check_end = models.BooleanField(default=False)

    def _perform_validation(self, reservation):
        if self.get_forbidden_periods(reservation.start, reservation.end, check_end=self.check_end):
            if self.interval_type == self.NOT_SOONER:
                raise TooSoon((self.time_unit, self.time_value))
            elif self.interval_type == self.NOT_LATER:
                raise TooLate((self.time_unit, self.time_value))
            else:
                raise AssertionError("Interval type must be 'l' or 's', '%s' given" % self.interval_type)

    def get_forbidden_periods(self, start, end, size=1, check_end=False):
        interval_params = (
            {'seconds': self.time_value}
            if self.time_unit == 'second' else
            {'seconds': self.time_value * 60}
            if self.time_unit == 'minute' else
            {'seconds': self.time_value * 3600}
            if self.time_unit == 'hour' else
            {'days': self.time_value}
            if self.time_unit == 'day' else
            None)

        if interval_params:
            interval = timedelta(**interval_params)
        else:
            raise ValueError("time_unit must be one of (second, minute, hour, day)")

        forbidden_periods = []

        if self.interval_type == self.NOT_SOONER and start < now() + interval:
            forbidden_periods.append((start, now() + interval))
        if self.interval_type == self.NOT_LATER and start > now() + interval:
            # if period in question starts after latest possible date return
            # immediately:
            return [(start, end)]
        if check_end and self.interval_type == self.NOT_LATER and end > now() + interval:
            forbidden_periods.append((now + interval, end))

        return forbidden_periods


class WithinPeriodValidator(Validator):
    """Make sure reservation is in one of given periods.

    This validator requires associated ``Period`` model.

    Validation is simply checking if reservation falls into any of allowed periods.

    """
    class Meta:
        abstract = True

    def _perform_validation(self, reservation):
        for period in self.periods.all():
            all_fields_valid_for_period = True
            for (date, field_name) in [(reservation.start, 'start'), (reservation.end, 'end')]:
                if (
                    (period.end and date > period.end)  # after end
                    or
                    (period.start and date < period.start)  # before start
                ):
                    all_fields_valid_for_period = False

            if all_fields_valid_for_period:
                return

        raise OutsideAllowedPeriods(list(self.periods.all()))


class Period(models.Model):
    """Period model for WithinPeriodValidator.

    In this model implementation it is obligatory to implement foreign key
    pointing to WithinPeriodValidator model with related name of "periods", e.g.:

    validator = models.ForeignKey('WithinPeriodValidator', related_name='periods')
    """

    class Meta:
        abstract = True

    start = models.DateTimeField(null=True, blank=True)
    end = models.DateTimeField(null=True, blank=True)

    def __unicode__(self):
        return "<%s, %s>" % (self.start, self.end)


class NotWithinPeriodValidator(Validator):
    """Make sure reservation is not in given period."""
    class Meta:
        abstract = True

    start = models.DateTimeField()
    end = models.DateTimeField()

    def _perform_validation(self, reservation):
        assert self.start <= self.end

        if reservation.start <= self.end and reservation.end >= self.start:
            raise ForbiddenPeriod(self.start, self.end)


class PeriodsInWeekdaysValidator(Validator):
    """Allow only reservation that fall into open hours pattern.

    This validator requires associated ``Period`` model."""

    class Meta:
        abstract = True

    def _perform_validation(self, reservation):
        required_period_params_list = self._construct_required_period_params_list(
            start=reservation.start,
            end=reservation.end
        )

        for required_period_params in required_period_params_list:
            if not self._check_required_period_params(required_period_params):
                raise ForbiddenHours(self.periods.all())

    def _check_required_period_params(self, period_params):
        for period in self.periods.all():
            if self._check_period_with_required_period_params(period, period_params):
                return True

        return False

    def _check_period_with_required_period_params(self, period, required_period_params):
        if period.weekday != required_period_params['weekday']:
            return False

        for time_val in [required_period_params['start'], required_period_params['end']]:
            if (
                (period.end and time_val > period.end)  # after end
                or
                (period.start and time_val < period.start)  # before start
            ):
                return False

        return True

    def _construct_required_period_params_list(self, start, end, already_constructed=None):
        if already_constructed is None:
            already_constructed = []

        if len(already_constructed) >= 8:
            return already_constructed

        period_params = {
            'weekday': start.weekday(),
            'start': start.time()
        }

        if start.day == end.day:
            period_params['end'] = end.time()
            already_constructed.append(period_params)
            return already_constructed
        else:
            period_params['end'] = time(23, 59, 59)
            already_constructed.append(period_params)
            new_start = datetime.combine(start.date(), time()) + timedelta(days=1)
            return self._construct_required_period_params_list(
                start=new_start,
                end=end,
                already_constructed=already_constructed
            )


class WithinDayPeriod(models.Model):
    """Period model for PeriodsInWeekdaysValidator.

    In this model implementation it is obligatory to implement foreign key
    pointing to PeriodsInWeekdaysValidator model with related name of "periods", e.g.:

    validator = models.ForeignKey('PeriodsInWeekdaysValidator', related_name='periods')
    """

    class Meta:
        abstract = True

    weekday = models.IntegerField()
    start = models.TimeField(null=True, blank=True)
    end = models.TimeField(null=True, blank=True)


class MaxDurationValidator(Validator):
    """Make sure reservation is not too long.

    Max duration is given is seconds.

    """
    class Meta:
        abstract = True

    max_duration_in_seconds = models.PositiveIntegerField()

    def _perform_validation(self, reservation):
        delta = (reservation.end - reservation.start)
        duration = delta.days * 3600 * 24 + delta.seconds

        if duration > self.max_duration_in_seconds:
            raise TooLong(self.max_duration_in_seconds)


class MaxReservationsPerUserValidator(Validator):
    """Make sure specific user doesn't have too many reservations.

    Requires `Reservation` model to have field `owner`, which can be virtually
    anything, as long as it uniquely identifies a user. Likely it will be
    foreign key to `User` model.

    Fields:
        max_reservations_on_current_subject :: PositiveSmallIntegerField
        max_reservations_on_all_subjects    :: PositiveSmallIntegerField
    """
    class Meta:
        abstract = True

    max_reservations_on_current_subject = models.PositiveSmallIntegerField(default=0, help_text="0 means no limit")
    max_reservations_on_all_subjects = models.PositiveSmallIntegerField(default=0, help_text="0 means no limit")

    def _perform_validation(self, reservation):
        if self.max_reservations_on_current_subject:
            reservations_so_far = reservation.subject.reservations.filter(
                end__gte=now(), owner=reservation.owner).count()
            if reservations_so_far >= self.max_reservations_on_current_subject:
                raise TooManyReservationsOnSubjectForUser(self.max_reservations_on_current_subject)
        if self.max_reservations_on_all_subjects:
            reservations_so_far = reservation.__class__.objects.filter(
                end__gte=now(), owner=reservation.owner).count()
            if reservations_so_far >= self.max_reservations_on_all_subjects:
                raise TooManyReservationsForUser(self.max_reservations_on_all_subjects)
