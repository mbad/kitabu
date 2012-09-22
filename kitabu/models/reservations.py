#-*- coding=utf-8 -*-

from django.db import models
from django.contrib.auth.models import User

from kitabu.utils import EnsureSize


class BaseReservation(models.Model, EnsureSize):
    class Meta:
        abstract = True

    owner = models.ForeignKey(User, null=True)
    start = models.DateTimeField()
    end = models.DateTimeField()


class ReservationWithSize(BaseReservation):
    class Meta:
        abstract = True

    size = models.IntegerField()
