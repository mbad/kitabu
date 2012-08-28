#-*- coding=utf-8 -*-

from collections import defaultdict

from django.db import models

from kitabu.exceptions import OverlappingReservations, CapacityExceeded


class BaseSubject(models.Model):
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


class FiniteCapacitySubject(BaseSubject):
    '''
    This mixin requires capacity property. Available e.g. in
    VariableCapacitySubject and FixedCapacitySubject
    '''
    class Meta:
        abstract = True

    def reserve(self, start, end, size, **kwargs):
        overlapping_reservations = self.reservations.filter(start__lt=end,
                                                            end__gt=start)
        if size > self.capacity:
            raise CapacityExceeded

        dates = defaultdict(lambda: 0)
        for r in overlapping_reservations:
            # mark when usage of subject changes
            dates[r.start] += getattr(r, 'size', 1)
            dates[r.end] -= getattr(r, 'size', 1)
        balance = 0
        for date, delta in sorted(dates.iteritems()):
            balance += delta
            if balance + size > self.capacity:
                raise CapacityExceeded

        super(FiniteCapacitySubject, self).reserve(start=start, end=end,
                size=size, **kwargs)


class VariableCapacitySubject(FiniteCapacitySubject):
    class Meta:
        abstract = True

    capacity = models.PositiveIntegerField()


class FixedCapacitySubject(FiniteCapacitySubject):
    '''
    You can inherit from this class like this:
    class YourClass(FixedCapacitySubject.with_capacity(5)
        pass
    '''
    class Meta:
        abstract = True

    @classmethod
    def with_capacity(cls, capacity):
        cls._capacity = capacity
        return cls

    @property
    def capacity(self):
        return self._capacity
