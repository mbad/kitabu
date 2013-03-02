from django.db import models
from django.contrib.auth.models import User

from kitabu.models.subjects import VariableSizeSubjectMixin, BaseSubject
from kitabu.models.reservations import ReservationMaybeExclusive, ReservationGroup, BaseReservation
from kitabu.models import validators

from pools.models import Pool


class Lane(VariableSizeSubjectMixin, BaseSubject):
    name = models.TextField()
    cluster = models.ForeignKey(Pool, related_name='lanes')

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


class LFullTimeValidator(validators.FullTimeValidator):
    pass


class LTimeIntervalValidator(validators.TimeIntervalValidator):
    pass


class LWithinPeriodValidator(validators.WithinPeriodValidator):
    pass


class Period(validators.Period):
    validator = models.ForeignKey(LWithinPeriodValidator, related_name='periods')


class LNotWithinPeriodValidator(validators.NotWithinPeriodValidator):
    pass


class LGivenHoursAndWeekdaysValidator(validators.GivenHoursAndWeekdaysValidator):
    pass


class LMaxReservationsPerUserValidator(validators.MaxReservationsPerUserValidator):
    pass
