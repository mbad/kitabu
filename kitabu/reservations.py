#-*- coding=utf-8 -*-

from django.db import models
from django.contrib.auth.models import User


class BaseReservation(models.Model):
    class Meta:
        abstract = True

    owner = models.ForeignKey(User, null=True)
    start = models.DateTimeField()
    end = models.DateTimeField()

    @classmethod
    def make_reservation(cls, start, end, subject, owner, **kwargs):
        return subject.reserve(start=start, end=end, owner=owner, **kwargs)


class ReservationWithSize(BaseReservation):
    class Meta:
        abstract = True

    size = models.IntegerField()

    @classmethod
    def make_reservation(cls, size, **kwargs):
        return super(ReservationWithSize, cls).make_reservation(
                                        size=size, **kwargs)
