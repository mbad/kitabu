from django.db import models
from django.contrib.auth.models import User

from reserver_exceptions import OverlappingReservations


class Reservable(object):
    owner = models.ForeignKey(User)

    def reserve(self, start, end, owner, **kwargs):
        self.reservations.create(start=start, end=end, owner=owner, **kwargs)
    
class GroupedReservable(Reservable):
    reservable_group = models.ForeignKey('ReservableGroup', null=True)

class ExclusiveReservable(Reservable):
    def reserve(self, start, end, **kwargs):
        overlapping_reservations = self.reservations.filter(start__lt=end, end__gt=start)
        if overlapping_reservations:
            raise OverlappingReservations(overlapping_reservations)
        else:
            return super(ExclusiveReservable, self).reserve(start, end, **kwargs)
