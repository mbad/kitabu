from django.db import models
from django.contrib.auth.models import User

from reserver.exceptions import OverlappingReservations


class Reservable(models.Model):
    class Meta:
        abstract = True
        app_label = 'changeme'

    owner = models.ForeignKey(User)

    def reserve(self, start, end, owner, **kwargs):
        self.reservations.create(start=start, end=end, owner=owner, **kwargs)

class GroupedReservable(Reservable):
    class Meta:
        abstract = True
        app_label = 'changeme'

    reservable_group = models.ForeignKey('ReservableGroup', null=True)

class ExclusiveReservable(Reservable):
    class Meta:
        abstract = True
        app_label = 'changeme'

    def reserve(self, start, end, **kwargs):
        overlapping_reservations = self.reservations.filter(start__lt=end, end__gt=start)
        if overlapping_reservations:
            raise OverlappingReservations(overlapping_reservations)
        else:
            return super(ExclusiveReservable, self).reserve(start, end, **kwargs)
