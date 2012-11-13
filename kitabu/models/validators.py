#-*- coding=utf-8 -*-

from importlib import import_module
from datetime import datetime

from django.db import models

from kitabu.exceptions import ValidationError

# using datetime.now in this way allows to mock it with mock.patch and test nicely
now = datetime.now


class Validator(models.Model):
    class Meta:
        app_label = 'kitabu'

    actual_validator_related_name = models.CharField(max_length=200)

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
        return ['start']


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


class NotSoonerThanValidator(Validator):
    class Meta:
        abstract = True

    date = models.DateTimeField()

    def _perform_validation(self, reservation):
        date_field_names = self._get_date_field_names()
        dates = [getattr(reservation, field_name) for field_name in date_field_names]
        assert all([isinstance(date, datetime) for date in dates])

        for (date, field_name) in zip(dates, date_field_names):
            if date < self.date:
                raise ValidationError("Reservation %s must not be earlier than %s" %
                                      (field_name, self.date))

    def _get_date_field_names(self):
        return ['start']


class FarEnoughValidator(Validator):
    class Meta:
        abstract = True

    TIME_UNITS = ['second', 'minute', 'hour', 'day']

    time_value = models.PositiveSmallIntegerField(default=1)
    time_unit = models.CharField(max_length=6, choices=[(x, x) for x in TIME_UNITS], default='second')

    def _perform_validation(self, reservation):
        date_field_names = self._get_date_field_names()
        dates = [getattr(reservation, field_name) for field_name in date_field_names]
        assert all([isinstance(date, datetime) for date in dates])

        for (date, field_name) in zip(dates, date_field_names):
            delta = date - now()

            too_soon = False

            if self.time_unit == 'second':
                if delta.total_seconds() < self.time_value:
                    too_soon = True
            elif self.time_unit == 'minute':
                if delta.total_seconds() < self.time_value * 60:
                    too_soon = True
            elif self.time_unit == 'hour':
                if delta.total_seconds() < self.time_value * 3600:
                    too_soon = True
            elif self.time_unit == 'day':
                if delta.days < self.time_value:
                    too_soon = True

            if too_soon:
                raise ValidationError("Reservation %s must by at least %s %ss in the future" %
                                      (field_name, self.time_value, self.time_unit))

    def _get_date_field_names(self):
        return ['start']
