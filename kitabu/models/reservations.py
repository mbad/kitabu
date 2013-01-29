#-*- coding=utf-8 -*-

from django.db import models, transaction

from kitabu.utils import EnsureSize, AtomicReserver


class BaseReservation(models.Model, EnsureSize):
    class Meta:
        abstract = True

    start = models.DateTimeField()
    end = models.DateTimeField()

    def __unicode__(self):
        return "id: %s, start: %s, end: %s" % (self.id, self.start, self.end)


class ReservationWithSize(models.Model):
    class Meta:
        abstract = True

    size = models.PositiveIntegerField()


class ApprovableReservation(models.Model):
    class Meta:
        abstract = True

    approved = models.BooleanField()
    valid_until = models.DateTimeField()


class ReservationMaybeExclusive(ReservationWithSize):
    class Meta:
        abstract = True

    exclusive = models.BooleanField(default=False)

    def __init__(self, *args, **kwargs):
        super(ReservationMaybeExclusive, self).__init__(*args, **kwargs)
        if self.exclusive:
            self.size = self.subject.size


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
