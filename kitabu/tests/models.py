from django.db import models
from kitabu.models.subjects import (BaseSubject, ExclusiveSubjectMixin, FixedSizeSubject, VariableSizeSubjectMixin,
                                    ExclusivableVariableSizeSubjectMixin, SubjectWithApprovableReservations)
from kitabu.models.reservations import (BaseReservation, ReservationWithSize, ReservationGroup,
                                        ReservationMaybeExclusive, ApprovableReservation)
from kitabu.models.clusters import BaseCluster
from kitabu.models.validators import (
    FullTimeValidator as KitabuFullTimeValidator,
    StaticValidator as KitabuStaticValidator,
    TimeIntervalValidator as KitabuTimeIntervalValidator,
    WithinPeriodValidator as KitabuWithinPeriodValidator,
    Period as KitabuPeriod,
    WithinDayPeriod as KitabuWithinDayPeriod,
    NotWithinPeriodValidator as KitabuNotWithinPeriodValidator,
    MaxDurationValidator as KitabuMaxDurationValidator,
    PeriodsInWeekdaysValidator as KitabuPeriodsInWeekdaysValidator,
    MaxReservationsPerUserValidator as KitabuMaxReservationsPerUserValidator,
)


class TennisCourt(ExclusiveSubjectMixin, BaseSubject):
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


class Room(VariableSizeSubjectMixin, BaseSubject):
    name = models.TextField()


# A different room class, for concurrent group reservations test
class OtherRoom(VariableSizeSubjectMixin, BaseSubject):
    name = models.TextField()


class TestReservationGroup(ReservationGroup):
    pass


class RoomReservation(ReservationWithSize, BaseReservation):
    subject = models.ForeignKey(Room, related_name='reservations')
    group = models.ForeignKey(TestReservationGroup, related_name='reservations', blank=True, null=True)


class OtherRoomReservation(ReservationWithSize, BaseReservation):
    subject = models.ForeignKey(OtherRoom, related_name='reservations')
    group = models.ForeignKey(TestReservationGroup, related_name='other_reservations', blank=True, null=True)


class Hotel(BaseCluster):
    pass


class HotelRoom(VariableSizeSubjectMixin, SubjectWithApprovableReservations, BaseSubject):
    cluster = models.ForeignKey(Hotel, related_name='rooms')
    name = models.TextField()


class HotelRoomReservation(ReservationWithSize, ApprovableReservation, BaseReservation):
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


class PeriodsInWeekdaysValidator(KitabuPeriodsInWeekdaysValidator):
    pass


class WithinDayPeriod(KitabuWithinDayPeriod):
    validator = models.ForeignKey(PeriodsInWeekdaysValidator, related_name='periods')


class ConferenceRoom(ExclusivableVariableSizeSubjectMixin, BaseSubject):
    pass


class ConferenceRoomReservation(ReservationMaybeExclusive, BaseReservation):
    subject = models.ForeignKey(ConferenceRoom, related_name='reservations')


class RoomWithApprovableReservations(VariableSizeSubjectMixin, SubjectWithApprovableReservations, BaseSubject):
    pass


class ApprovableRoomReservation(ReservationWithSize, ApprovableReservation, BaseReservation):
    subject = models.ForeignKey(RoomWithApprovableReservations, related_name='reservations')


class Table(BaseSubject):
    pass


class TableReservation(BaseReservation):
    subject = models.ForeignKey(Table, related_name='reservations')
    owner = models.CharField(max_length=20)


class MaxReservationsPerUserValidator(KitabuMaxReservationsPerUserValidator):
    pass
