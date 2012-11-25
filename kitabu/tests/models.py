from django.db import models
from kitabu.models.subjects import ExclusiveSubject, FixedSizeSubject, VariableSizeSubject
from kitabu.models.reservations import BaseReservation, ReservationWithSize, ReservationGroup
from kitabu.models.clusters import BaseCluster
from kitabu.models.validators import (
    FullTimeValidator as KitabuFullTimeValidator,
    StaticValidator as KitabuStaticValidator,
    LateEnoughValidator as KitabuFarEnoughValidator,
    NotSoonerThanValidator as KitabuNotSoonerThanValidator,
    NotLaterThanValidator as KitabuNotLaterThanValidator,
    WithinPeriodValidator as KitabuWithinPeriodValidator,
    NotWithinPeriodValidator as KitabuNotWithinPeriodValidator,
    MaxDurationValidator as KitabuMaxDurationValidator,
    GivenHoursAndDaysValidator as KitabuGivenHoursAndDaysValidator
)


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


class RoomReservationGroup(ReservationGroup):
    pass


class RoomReservation(ReservationWithSize):
    subject = models.ForeignKey(Room, related_name='reservations')
    group = models.ForeignKey(RoomReservationGroup, related_name='reservations', blank=True, null=True)


class Hotel(BaseCluster):
    pass


class HotelRoom(VariableSizeSubject):
    cluster = models.ForeignKey(Hotel, related_name='rooms')
    name = models.TextField()


class HotelRoomReservation(ReservationWithSize):
    subject = models.ForeignKey(HotelRoom, related_name='reservations')


class FullTimeValidator(KitabuFullTimeValidator):
    pass


class StaticValidator(KitabuStaticValidator):
    pass


class LateEnoughValidator(KitabuFarEnoughValidator):
    pass


class NotSoonerThanValidator(KitabuNotSoonerThanValidator):
    pass


class NotLaterThanValidator(KitabuNotLaterThanValidator):
    pass


class WithinPeriodValidator(KitabuWithinPeriodValidator):
    pass


class NotWithinPeriodValidator(KitabuNotWithinPeriodValidator):
    pass


class MaxDurationValidator(KitabuMaxDurationValidator):
    pass


class GivenHoursAndDaysValidator(KitabuGivenHoursAndDaysValidator):
    pass
