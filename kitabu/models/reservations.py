#-*- coding=utf-8 -*-

import datetime
import warnings

from django.db import models, transaction

from kitabu.utils import EnsureSize, AtomicReserver
from kitabu.models.managers import ApprovableReservationsManager

now = datetime.datetime.now


class BaseReservation(models.Model, EnsureSize):
    """Base reservation class.

    It represents a reservation on a subject that has a start and end
    which are datetime instances.

    When subclassing in a project an additional field is required, namely
    subject. This is not provided out of the box, to allow programmer specify
    arbitrary subject of reservation, not limited by framework.

    Provided fields:

        start :: DateTimeField
        end   :: DateTimeField

    Provided methods:
        is_valid

    Provided class methods:
        colliding_reservations
        colliding_reservations_in_subjects
        colliding_reservations_in_clusters
    """
    class Meta:
        abstract = True

    start = models.DateTimeField(db_index=True)
    end = models.DateTimeField(db_index=True)

    def is_valid(self):
        """Indicate if the reservation is valid. Alway true in this class."""
        return True

    def __unicode__(self):
        return "id: %s, start: %s, end: %s" % (self.id, self.start, self.end)

    # TODO: According to django design practices the following 3 methods should
    # be methods on manager, not model.
    @classmethod
    def colliding_reservations_in_subjects(cls, start, end, subjects, *args, **kwargs):
        """Return reservations on ``subjects`` that overlap <start, end> period.
        """
        kwargs['subject__in'] = subjects
        return cls.colliding_reservations(start=start, end=end, *args, **kwargs)

    @classmethod
    def colliding_reservations_in_clusters(cls, start, end, clusters, *args, **kwargs):
        """Return reservations on ``clusters`` that overlap <start, end> period.
        """
        kwargs['subject__cluster_id__in'] = clusters
        return cls.colliding_reservations(start=start, end=end, *args, **kwargs)

    @classmethod
    def colliding_reservations(cls, start, end, *args, **kwargs):
        """Return reservations on ``clusters`` that overlap <start, end> period.
        """
        return cls.objects.filter(start__lt=end, end__gt=start, *args, **kwargs)


class ApprovableReservation(models.Model):
    #TODO: this description goes before all that is described is implemented.
    # Verify after implementing all of this.
    """Mixin for BaseReservation adding approval functionality.

    Meant for use with SubjectWithApprovableReservations.

    Adds two model fields:

        approved :: BooleanField
        valid_until :: DateTimeField

    ``valid_until`` is filled either automatically, using
    ``settings.DEFAULT_TIME_FOR_APPROVAL`` variable or manually by providing
    TODO argument to ``Subject.reserve`` method.

    Overrides default manager to filter out outdated reservations that didn't
    get approved.

    """
    class Meta:
        abstract = True

    objects = ApprovableReservationsManager()

    approved = models.BooleanField(default=True, db_index=True)
    valid_until = models.DateTimeField(null=True, db_index=True)

    def is_valid(self):
        """Return True, unless reservation is not aproved and outdated."""
        return self.approved or self.valid_until > now()

    def approve(self):
        """Mark reservation as approved and save it."""
        self.approved = True
        self.save()


class ReservationWithSize(models.Model):
    """Mixin for BaseReservation providing size field."""
    class Meta:
        abstract = True

    size = models.PositiveIntegerField()


class ReservationMaybeExclusive(ReservationWithSize):
    """Subclass of ReservationWithSize that allows exclusiveness.

    If reservation is exclusive, flag ``exclusive`` is set on it and its
    ``size`` is set to maximum for subject in question. Explicit setting of
    ``size`` is then forbidden.

    Provides one additional field:

        exclusive :: BooleanField

    To make sure that changing size of related subject won't break the
    exclusive reservation functionality, use ExclusivableVariableSizeSubjectMixin
    that will update all exclusive reservation when size of subject is changed.
    """
    class Meta:
        abstract = True

    exclusive = models.BooleanField(default=False, db_index=True)

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
    """Group of reservations that are treated together.

    Main goal is to provide a way to reserve *all of them at once* or
    *all of them or none*. This is achieved by making all reservations in one
    transaction.

    Additional gain is that the reservation can be easily managed together,
    thanks to being tied in one group.

    This may be of use e.g. for cancelling or approving logically linked group
    of reservations.

    """
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
