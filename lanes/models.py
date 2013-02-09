from django.db import models
from django.contrib.auth.models import User

from kitabu.models.subjects import VariableSizeSubject, BaseSubject
from kitabu.models.reservations import ReservationMaybeExclusive, ReservationGroup, BaseReservation
from kitabu.models import validators

from pools.models import Pool


class Lane(VariableSizeSubject, BaseSubject):
    name = models.TextField()
    cluster = models.ForeignKey(Pool, related_name='subjects')

    def __unicode__(self):
        return self.name


class LaneReservation(ReservationMaybeExclusive, BaseReservation):
    subject = models.ForeignKey('Lane', related_name='reservations')
    group = models.ForeignKey('LaneReservationGroup', related_name='reservations', null=True, blank=True)
    owner = models.ForeignKey(User, null=True)

    def __unicode__(self):
        return "%s from %s to %s (%s places)" % (self.subject.name, self.start, self.end, self.size)


class LaneReservationGroup(ReservationGroup):
    pass


class LaneFullTimeValidator(validators.FullTimeValidator):
    pass


class LaneTimeIntervalValidator(validators.TimeIntervalValidator):
    pass


class LaneWithinPeriodValidator(validators.WithinPeriodValidator):
    pass


class LaneNotWithinPeriodValidator(validators.NotWithinPeriodValidator):
    pass


class LaneGivenHoursAndWeekdaysValidator(validators.GivenHoursAndWeekdaysValidator):
    pass
