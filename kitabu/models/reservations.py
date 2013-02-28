#-*- coding=utf-8 -*-
import datetime
import warnings

from django.db import models, transaction

from kitabu.utils import EnsureSize, AtomicReserver
from kitabu.models.managers import ApprovableReservationsManager


class BaseReservation(models.Model, EnsureSize):
    class Meta:
        abstract = True

    start = models.DateTimeField()
    end = models.DateTimeField()

    def is_valid(self):
        return True

    def __unicode__(self):
        return "id: %s, start: %s, end: %s" % (self.id, self.start, self.end)

    @classmethod
    def colliding_reservations_in_subjects(cls, start, end, subjects, *args, **kwargs):
        kwargs['subject__cluster_id__in'] = subjects
        return cls.colliding_reservations(start=start, end=end, *args, **kwargs)

    @classmethod
    def colliding_reservations_in_clusters(cls, start, end, clusters, *args, **kwargs):
        kwargs['subject__cluster_id__in'] = clusters
        return cls.colliding_reservations(start=start, end=end, *args, **kwargs)

    @classmethod
    def colliding_reservations(cls, start, end, *args, **kwargs):
        return cls.objects.filter(start__lt=end, end__gt=start, *args, **kwargs)


class ReservationWithSize(models.Model):
    class Meta:
        abstract = True

    size = models.PositiveIntegerField()


class ApprovableReservation(models.Model):
    class Meta:
        abstract = True

    objects = ApprovableReservationsManager()

    approved = models.BooleanField(default=True)
    valid_until = models.DateTimeField(null=True)

    def is_valid(self):
        return self.approved or self.valid_until > datetime.datetime.now()

    def approve(self):
        self.approved = True
        self.save()


class ReservationMaybeExclusive(ReservationWithSize):
    class Meta:
        abstract = True

    exclusive = models.BooleanField(default=False)

    def __init__(self, *args, **kwargs):
        super(ReservationMaybeExclusive, self).__init__(*args, **kwargs)
        if self.exclusive:
            self.__dict__['size'] = self.subject.size
            if 'size' in kwargs:
                warnings.warn("Explicitely setting size for exclusive reservation is ignored")

    def __setattr__(self, name, value):
        if name == 'size' and getattr(self, 'size', False) and getattr(self, 'exclusive', False):
            raise AttributeError('Cannot explicitely change size of exclusive reservation')
        super(ReservationMaybeExclusive, self).__setattr__(name, value)

    def save(self, *args, **kwargs):
        super(ReservationMaybeExclusive, self).save(*args, **kwargs)
        if self.exclusive:
            self.__dict__['size'] = self.subject.size


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
