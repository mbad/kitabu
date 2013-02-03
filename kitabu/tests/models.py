from django.db import models
from kitabu.models.subjects import (BaseSubject, ExclusiveSubject, FixedSizeSubject, VariableSizeSubject,
                                    SubjectWithApprovableReservations)
from kitabu.models.reservations import (BaseReservation, ReservationWithSize, ReservationGroup,
                                        ReservationMaybeExclusive, ApprovableReservation)
from kitabu.models.clusters import BaseCluster
from kitabu.models.validators import (
    FullTimeValidator as KitabuFullTimeValidator,
    StaticValidator as KitabuStaticValidator,
    TimeIntervalValidator as KitabuTimeIntervalValidator,
    WithinPeriodValidator as KitabuWithinPeriodValidator,
    Period as KitabuPeriod,
    NotWithinPeriodValidator as KitabuNotWithinPeriodValidator,
    MaxDurationValidator as KitabuMaxDurationValidator,
    GivenHoursAndWeekdaysValidator as KitabuGivenHoursAndWeekdaysValidator,
)


class TennisCourt(ExclusiveSubject, BaseSubject):
    '''
    An ExlusiveSubject example
    '''
    name = models.TextField()


class CourtReservation(BaseReservation):
    subject = models.ForeignKey(TennisCourt, related_name='reservations')


class FiveSeatsBus(FixedSizeSubject.with_size(5), BaseSubject):
    name = models.TextField()


class BusReservation(ReservationWithSize, BaseReservation):
    subject = models.ForeignKey(FiveSeatsBus, related_name='reservations')


class Room(VariableSizeSubject, BaseSubject):
    name = models.TextField()


class RoomReservationGroup(ReservationGroup):
    pass


class RoomReservation(ReservationWithSize, BaseReservation):
    subject = models.ForeignKey(Room, related_name='reservations')
    group = models.ForeignKey(RoomReservationGroup, related_name='reservations', blank=True, null=True)


class Hotel(BaseCluster):
    pass


class HotelRoom(VariableSizeSubject, BaseSubject):
    cluster = models.ForeignKey(Hotel, related_name='rooms')
    name = models.TextField()


class HotelRoomReservation(ReservationWithSize, BaseReservation):
    subject = models.ForeignKey(HotelRoom, related_name='reservations')


class FullTimeValidator(KitabuFullTimeValidator):
    pass


class StaticValidator(KitabuStaticValidator):
    pass


class TimeIntervalValidator(KitabuTimeIntervalValidator):
    pass


class WithinPeriodValidator(KitabuWithinPeriodValidator):
    pass


class Period(KitabuPeriod):
    validator = models.ForeignKey(WithinPeriodValidator, related_name='periods')


class NotWithinPeriodValidator(KitabuNotWithinPeriodValidator):
    pass


class MaxDurationValidator(KitabuMaxDurationValidator):
    pass


class GivenHoursAndWeekdaysValidator(KitabuGivenHoursAndWeekdaysValidator):
    pass


class ConferenceRoom(VariableSizeSubject, BaseSubject):
    pass


class ConferenceRoomReservation(ReservationMaybeExclusive, BaseReservation):
    subject = models.ForeignKey(ConferenceRoom, related_name='reservations')


class RoomWithApprovableReservations(VariableSizeSubject, SubjectWithApprovableReservations, BaseSubject):
    pass


class ApprovableRoomReservation(ReservationWithSize, ApprovableReservation, BaseReservation):
    subject = models.ForeignKey(RoomWithApprovableReservations, related_name='reservations')
