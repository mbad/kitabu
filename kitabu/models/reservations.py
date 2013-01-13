#-*- coding=utf-8 -*-

from django.db import models, transaction

from kitabu.utils import EnsureSize, AtomicReserver


class BaseReservation(models.Model, EnsureSize):
    class Meta:
        abstract = True

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
            AtomicReserver.non_transactional_reserve(*args, group=group, **kwargs)
            transaction.commit()
            return group
        except:
            transaction.rollback()
            raise
