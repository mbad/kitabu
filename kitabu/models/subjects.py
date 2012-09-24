#-*- coding=utf-8 -*-

from collections import defaultdict

from django.db import models

from kitabu.exceptions import OverlappingReservations, SizeExceeded
from kitabu.utils import EnsureSize

from managers import SubjectManager


class BaseSubject(models.Model, EnsureSize):
    objects = SubjectManager()

    class Meta:
        abstract = True

    def reserve(self, **kwargs):
        Reservation = self.reservation_model
        return Reservation.objects.create(subject=self, **kwargs)

    @classmethod
    def get_reservation_model(cls):
        return cls._meta.get_field_by_name('reservations')[0].model

    @property
    def reservation_model(self):
        return self.__class__.get_reservation_model()


class ExclusiveSubject(BaseSubject):
    class Meta:
        abstract = True

    def reserve(self, start, end, **kwargs):
        overlapping_reservations = self.reservations.filter(start__lt=end,
                                                            end__gt=start)
        if overlapping_reservations:
            raise OverlappingReservations(overlapping_reservations)
        else:
            return super(ExclusiveSubject, self).reserve(start=start, end=end,
                                                         **kwargs)


class FiniteSizeSubject(BaseSubject):
    '''
    This mixin requires size property. Available e.g. in
    VariableSizeSubject and FixedSizeSubject
    '''
    class Meta:
        abstract = True

    def reserve(self, start, end, size, **kwargs):
        overlapping_reservations = self.reservations.filter(start__lt=end,
                                                            end__gt=start)
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

        return super(FiniteSizeSubject, self).reserve(start=start, end=end,
                size=size, **kwargs)


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
        cls._size = size
        return cls

    @property
    def size(self):
        return self._size
