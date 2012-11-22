from kitabu.models.subjects import VariableSizeSubject
from kitabu.models.reservations import ReservationWithSize, ReservationGroup
from kitabu.models import validators
from django.db import models
from pools.models import Pool


class LaneFullTimeValidator(validators.FullTimeValidator):
    pass


class LaneNotSoonerThanValidator(validators.NotSoonerThanValidator):
    pass


class LaneNotLaterThanValidator(validators.NotLaterThanValidator):
    pass


class LaneLateEnoughValidator(validators.LateEnoughValidator):
    pass


class LaneWithinPeriodValidator(validators.WithinPeriodValidator):
    pass


class LaneNotWithinPeriodValidator(validators.NotWithinPeriodValidator):
    pass


class Lane(VariableSizeSubject):
    name = models.TextField()
    cluster = models.ForeignKey(Pool, related_name='subjects')

    def __unicode__(self):
        return self.name


class LaneReservation(ReservationWithSize):
    subject = models.ForeignKey('Lane', related_name='reservations')
    group = models.ForeignKey('LaneReservationGroup', related_name='reservations', null=True, blank=True)

    def __unicode__(self):
        return "%s from %s to %s (%s places)" % (self.subject.name, self.start, self.end, self.size)


class LaneReservationGroup(ReservationGroup):
    pass
