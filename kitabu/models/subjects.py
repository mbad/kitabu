#-*- coding=utf-8 -*-

from collections import defaultdict

from django.db import models
from django.db.models import Q

from kitabu.exceptions import SizeExceeded, ValidationError
from kitabu.utils import EnsureSize
from kitabu.models.validators import Validator

import datetime


class BaseSubject(models.Model, EnsureSize):
    class Meta:
        abstract = True

    validators = models.ManyToManyField(Validator, blank=True)

    def reserve(self, **kwargs):
        reservation = self.reservation_model(subject=self, **kwargs)
        self._validate_reservation(reservation)
        if kwargs.get('exclusive') or self._only_exclusive_reservations():
            self._validate_exclusive(reservation)
        reservation.save()
        return reservation

    def overlapping_reservations(self, start, end):
        return self.reservations.filter(start__lt=end, end__gt=start)

    @classmethod
    def get_reservation_model(cls):
        return cls._meta.get_field_by_name('reservations')[0].model

    @property
    def reservation_model(self):
        return self.__class__.get_reservation_model()

    # Private

    def _validate_reservation(self, reservation):

        for validator in Validator.universal.all():
            validator.validate(reservation)

        for validator in self.validators.all():
            validator.validate(reservation)

    def _validate_exclusive(self, reservation):
        # TODO: perhaps this would make sense to extract it as a static validator
        overlapping_reservations = self.overlapping_reservations(reservation.start, reservation.end)
        if overlapping_reservations:
            raise ValidationError("Overlapping reservations: %s" % overlapping_reservations)

    def _only_exclusive_reservations(self):
        return False


class SubjectWithApprovableReservations(models.Model):
    class Meta:
        abstract = True

    def overlapping_reservations(self, start, end):
        extra_filter = Q(approved=True) | Q(valid_until__gt=datetime.datetime.utcnow())
        return self.reservations.filter(extra_filter, start__lt=end, end__gt=start)

    def make_pre_reservation(self, start=None, end=None, valid_until=None, **kwargs):
        return self.reserve(start=start, end=end, valid_until=valid_until, approved=False, **kwargs)


class ExclusiveSubject(models.Model):
    class Meta:
        abstract = True

    def _only_exclusive_reservations(self):
        return True


class FiniteSizeSubject(models.Model):
    '''
    This mixin requires size property. Available e.g. in
    VariableSizeSubject and FixedSizeSubject
    '''
    class Meta:
        abstract = True

    def reserve(self, start=None, end=None, size=1, **kwargs):
        assert start and end, "start and end dates must be provided"
        overlapping_reservations = self.overlapping_reservations(start, end)
        if size > self.size:
            raise SizeExceeded

        dates = defaultdict(lambda: 0)
        for r in overlapping_reservations:
            # mark when usage of subject changes
            dates[r.start] += getattr(r, 'size', 1)
            dates[r.end] -= getattr(r, 'size', 1)
        balance = 0
        for date, delta in sorted(dates.iteritems()):
            balance += delta
            if balance + size > self.size:
                raise SizeExceeded

        return super(FiniteSizeSubject, self).reserve(start=start, end=end, size=size, **kwargs)


class VariableSizeSubject(FiniteSizeSubject):
    class Meta:
        abstract = True

    size = models.PositiveIntegerField()


class FixedSizeSubject(FiniteSizeSubject):
    '''
    You can inherit from this class like this:
    class YourClass(FixedSizeSubject.with_size(5)
        pass
    '''
    class Meta:
        abstract = True

    @classmethod
    def with_size(cls, size):
        # TODO: fix this, class should not be modified
        class C(cls):
            _size = size

            class Meta:
                abstract = True
        return C

    @property
    def size(self):
        return self._size
