#-*- coding=utf-8 -*-

from django.db import models
from django.contrib.auth.models import User

from exceptions import OverlappingReservations


class BaseSubject(models.Model):
    class Meta:
        abstract = True

    owner = models.ForeignKey(User)

    def reserve(self, start, end, owner, **kwargs):
        self.reservations.create(start=start, end=end, owner=owner, **kwargs)


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
            return super(ExclusiveSubject, self).reserve(start, end, **kwargs)
