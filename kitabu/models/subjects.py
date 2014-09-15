#-*- coding=utf-8 -*-

from collections import defaultdict

from django.db import models, transaction
from django.db.models import Q

from django.conf import settings

from kitabu.exceptions import (
    SizeExceeded,
    OverlappingReservations,
)
from kitabu.utils import EnsureSize
from kitabu.models.validators import Validator

import datetime
from time import sleep
from django.utils import timezone

now = timezone.now


class BaseSubject(models.Model, EnsureSize):
    """Base model for all Subjects.

    The main purpose of this class is to deliver ``reserve`` method that is
    intended to be called instead of creating reservation explicitly.

    It has one ``ManyToManyField`` - ``validators``.

    It is subclassed to deliver more specialized functionalities.

    By itself the class represents subject that can be reserved but includes no
    additional info about the subject, except for validators that can be
    attached.

    """
    class Meta:
        abstract = True

    validators = models.ManyToManyField(Validator, blank=True)

    @transaction.commit_manually
    def reserve(self, **kwargs):
        try:
            reservation = self.reserve_without_transaction(**kwargs)
            transaction.commit()
            return reservation
        except:
            transaction.rollback()
            raise

    def reserve_without_transaction(self, **kwargs):
        if settings.SECURE_RESERVATIONS:
            # explicitly lock this subject before reserving it
            list(self.__class__.objects.select_for_update().filter(pk=self.pk))
        return self.create_reservation(**kwargs)

    def create_reservation(self, **kwargs):
        """Make a reservation on current subject and return the reservation.

        The core method of Subject. Creates a reservation and validates
        it against all attached and global validators. If validation is
        successfull then reservation is saved to database and returned.
        Otherwise ``ReservationError`` is raised.

        """
        assert kwargs.get('start') and kwargs.get('end'), "start and end dates must be provided"

        delay_time = kwargs.pop('delay_time', None)

        reservation = self.reservation_model(subject=self, **kwargs)
        self._validate_reservation(reservation)
        if kwargs.get('exclusive') or self._only_exclusive_reservations():
            self._validate_exclusive(reservation)
        reservation.save()
        if delay_time:
            sleep(delay_time)
        return reservation

    def overlapping_reservations(self, start, end):
        """Find all reservations that overlap with given period.

        Return a query set, possibly empty.
        """
        return self.reservations.filter(start__lt=end, end__gt=start)

    @classmethod
    def get_reservation_model(cls):
        """Get class of reservation model associated with the Subject model."""
        return cls._meta.get_field_by_name('reservations')[0].model

    @property
    def reservation_model(self):
        """Get class of reservation model associated with the Subject model."""
        return self.__class__.get_reservation_model()

    # Private

    def _validate_reservation(self, reservation):
        """Run associated and global validators."""

        for validator in Validator.universal.all():
            validator.validate(reservation)

        for validator in self.validators.all():
            validator.validate(reservation)

    def _validate_exclusive(self, reservation):
        """Make sure given reservation's period doesn't overlap any other's.

        If there is overlapped reservation, raise ``OverlappingReservations``,
        otherwise do nothing.

        """
        overlapping_reservations = self.overlapping_reservations(reservation.start, reservation.end)
        if overlapping_reservations:
            raise OverlappingReservations(reservation, overlapping_reservations)

    def _only_exclusive_reservations(self):
        return False


class SubjectWithApprovableReservations(models.Model):

    """Subject for reservations that require approval - ``ApprovableReservation``s.

    Main purpose of this class is to modify ``reserve`` method to creat
    e reservation that still needs to be approved, otherwise will expire.

    Overrides method ``overlapping_reservations`` to discard not approved
    and thus no longer valid reservations.

    """

    validity_period = models.CharField(
        default=getattr(settings, "KITABU_DEFAULT_VALIDITY_PERIOD", "60*60*24*3"),
        max_length=13,
        help_text="How long can reservation on this subject wait for approval. "
                  "You can use digits and ``*`` sign to multiply."
    )

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        map(int, self.validity_period.split("*"))  # just don't save garbage
        return super(SubjectWithApprovableReservations, self).save(*args, **kwargs)

    def overlapping_reservations(self, start, end):
        """
        Find overlapping reservation discarding not approved and stale ones.
        """
        extra_filter = Q(approved=True) | Q(valid_until__gt=now())
        return self.reservations.filter(extra_filter, start__lt=end, end__gt=start)

    # def make_preliminary_reservation(self, valid_until, start=None, end=None, **kwargs):
    def create_reservation(self, valid_until=None, validity_period=None, approved=False, **kwargs):

        assert int(bool(valid_until)) + int(bool(validity_period)) + int(approved) <= 1, (
            "Supply no more than one of the following arguments: valid_until, validity_period, approved. "
            "Given (%s, %s, %s)." % (valid_until, validity_period, approved))

        if not approved:
            if valid_until:
                pass
            elif validity_period:
                valid_until = now() + validity_period
            else:
                valid_until = now() + self.validity_timedelta()

        return super(SubjectWithApprovableReservations, self).create_reservation(
            valid_until=valid_until, approved=approved, **kwargs)

    def validity_timedelta(self):
        validity_period_as_seconds = reduce(lambda acc, x: acc * int(x), self.validity_period.split("*"), 1)
        return datetime.timedelta(seconds=validity_period_as_seconds)


class ExclusiveSubjectMixin(models.Model):
    """Mixin that allows only exclusive reservations.

    Mixin before BaseSubject.
    Can be used with BaseReservation.

    """
    class Meta:
        abstract = True

    def _only_exclusive_reservations(self):
        return True


class FiniteSizeSubjectMixin(models.Model):
    '''Suitable for all subjects that can have limited concurrent reservations.

    This mixin requires size property. Available e.g. in VariableSizeSubjectMixin
    and FixedSizeSubject subclasses.

    Mix in before BaseSubject.

    '''
    class Meta:
        abstract = True

    def create_reservation(self, start=None, end=None, **kwargs):
        """Make a reservation on current subject and return the reservation.

        Check if reservation with given number of slots can be made. If yes,
        return super. If not raise SizeExceeded.

        """
        size = kwargs.get('size', 1)
        assert start and end, "start and end dates must be provided"
        assert size > 0, "size must be greater than zero"

        if size > self.size:
            raise SizeExceeded(subject=self, requested_size=size, start=start, end=end)

        overlapping_reservations = self.overlapping_reservations(start, end)

        dates = defaultdict(lambda: 0)
        for r in overlapping_reservations:
            # mark when usage of subject changes
            dates[r.start] += getattr(r, 'size', 1)
            dates[r.end] -= getattr(r, 'size', 1)
        balance = 0
        for date, delta in sorted(dates.iteritems()):
            balance += delta
            if balance + size > self.size:
                raise SizeExceeded(
                    subject=self,
                    requested_size=size,
                    start=start,
                    end=end,
                    overlapping_reservations=overlapping_reservations
                )

        return super(FiniteSizeSubjectMixin, self).create_reservation(start=start, end=end, **kwargs)


class FixedSizeSubject(FiniteSizeSubjectMixin):
    """Include functionality of FiniteSizeSubjectMixin and supply fixed size.

    This class can be inherited from like this:
    class YourClass(FixedSizeSubject.with_size(5)
        pass

    """
    class Meta:
        abstract = True

    @classmethod
    def with_size(cls, size):
        class C(cls):
            _size = size

            class Meta:
                abstract = True
        return C

    @property
    def size(self):
        return self._size


class VariableSizeSubjectMixin(FiniteSizeSubjectMixin):
    """Include functionality of FiniteSizeSubjectMixin and supply size field.

    ``size`` is simply django PositiveIntegerField, so each instance of this
    model can have its own size. Suitable for e.g. hotel rooms, where each
    can have different number of beds.

    """
    class Meta:
        abstract = True

    size = models.PositiveIntegerField()


class ExclusivableVariableSizeSubjectMixin(VariableSizeSubjectMixin):
    """Include functionality of VariableSizeSubjectMixin and watch data consistency.

    The main purpose of this mixin is to make sure that changing size of the
    subject will also change size of already made exclusive reservations and
    thus keep data consistent.

    As bonus it prevents programmer from accidentally setting size on exclusive
    reservation.
    """
    class Meta:
        abstract = True

    def __setattr__(self, name, value):
        if name == 'size' and getattr(self, '_old_size', None) is None:
            self._old_size = self.size
        return super(ExclusivableVariableSizeSubjectMixin, self).__setattr__(name, value)

    def save(self, **kwargs):
        super(ExclusivableVariableSizeSubjectMixin, self).save(**kwargs)

        if getattr(self, '_old_size', self.size) != self.size:  # if size has changed
            self.reservation_model.objects.filter(end__gte=now(), exclusive=True).update(size=self.size)
            delattr(self, '_old_size')

    def create_reservation(self, start=None, end=None, **kwargs):
        """Forbid exclusive reservation with size set, then call super."""
        if 'size' in kwargs and kwargs.get('exclusive'):
            raise AttributeError('Cannot explicitly set size for exclusive reservation')
        return super(ExclusivableVariableSizeSubjectMixin, self).create_reservation(start=start, end=end, **kwargs)
