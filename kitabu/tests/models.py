from django.db import models
from kitabu.models.subjects import ExclusiveSubject, FixedSizeSubject, VariableSizeSubject
from kitabu.models.reservations import BaseReservation, ReservationWithSize
from kitabu.models.clusters import BaseCluster


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


class Hotel(BaseCluster):
    pass


class HotelRoom(VariableSizeSubject):
    cluster = models.ForeignKey(Hotel, related_name='rooms')
    name = models.TextField()


class HotelRoomReservation(ReservationWithSize):
    subject = models.ForeignKey(HotelRoom, related_name='reservations')
