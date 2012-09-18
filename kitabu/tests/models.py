from django.db import models
from kitabu.models.subjects import ExclusiveSubject, FixedSizeSubject, VariableSizeSubject
from kitabu.models.reservations import BaseReservation, ReservationWithSize


class TennisCourt(ExclusiveSubject):
    '''
    An ExlusiveSubject example
    '''
    name = models.TextField()


class CourtReservation(BaseReservation):
    subject = models.ForeignKey(TennisCourt, related_name='reservations')


class FiveSeatsBus(FixedSizeSubject.with_size(5)):
    name = models.TextField()


class BusReservation(ReservationWithSize):
    subject = models.ForeignKey(FiveSeatsBus, related_name='reservations')


class Room(VariableSizeSubject):
    name = models.TextField()


class RoomReservation(ReservationWithSize):
    subject = models.ForeignKey(Room, related_name='reservations')
