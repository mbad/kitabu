#-*- coding=utf-8 -*-

from django.db import models, transaction
from django.contrib.auth.models import User

from kitabu.utils import EnsureSize, AtomicReserver


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


class ReservationGroup(models.Model):
    class Meta:
        abstract = True

    @classmethod
    @transaction.commit_manually
    def reserve(cls, *args, **kwargs):
        group = cls.objects.create()
        try:
            AtomicReserver._non_transactional_reserve(*args, group=group, **kwargs)
            transaction.commit()
            return group
        except:
            transaction.rollback()
            raise
