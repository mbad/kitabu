#-*- coding=utf-8 -*-

from collections import defaultdict

from django.db import models
#from django.contrib.auth.models import User

from exceptions import OverlappingReservations, CapacityExceeded


class BaseSubject(models.Model):
    class Meta:
        abstract = True

    def reserve(self, **kwargs):
        Reservation = self._meta.get_field_by_name('reservations')[0].model
        return Reservation.objects.create(subject=self, **kwargs)


class GroupableSubject(BaseSubject):
    class Meta:
        abstract = True

    cluster = models.ForeignKey('Cluster', null=True)


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
    VariableCapacitySubjectMixin
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
