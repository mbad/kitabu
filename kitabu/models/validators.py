#-*- coding=utf-8 -*-

from datetime import datetime
from django.db import models

from kitabu.exceptions import ValidationError


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

    INTERVAL_TYPES = ['second', 'minute', 'hour', 'day']

    interval = models.PositiveSmallIntegerField()
    interval_type = models.CharField(max_length=6, choices=[(x, x) for x in INTERVAL_TYPES])

    def _perform_validation(self, reservation):
        date_fields = self._get_date_fields()
        assert all([isinstance(getattr(reservation, date_field))
                    for date_field in date_fields]), "FullTimeValidator requires 'date' " \
                                                     "keyword argument which is datetime instance"

        def _validate_one(date, interval_type, interval):
            if self.interval_type == interval_type:
                if getattr(date, interval_type) % self.interval > 0:
                    raise ValidationError("%ss must by divisible by %s (%s is not)" %
                                          (interval_type, self.interval, interval))
            elif getattr(date, interval_type) > 0:
                raise ValidationError("%ss must by 0 (got %s)" %
                                      (interval_type, interval))

        for date_field in date_fields:
            date = getattr(reservation, date_field)
            for param in ['microsecond'] + self.INTERVAL_TYPES:
                interval = getattr(date, param)
                _validate_one(date, param, interval)
                if param == self.interval_type:
                    break

    def _get_date_fields(self):
        return ['start']
