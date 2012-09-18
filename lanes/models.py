from kitabu.models.subjects import VariableSizeSubject
from kitabu.models.reservations import ReservationWithSize
from django.db import models
from pools.models import Pool


class Lane(VariableSizeSubject):
    name = models.TextField()
    cluster = models.ForeignKey(Pool, related_name='subjects')

    def __unicode__(self):
        return self.name


class LaneReservation(ReservationWithSize):
    subject = models.ForeignKey('Lane', related_name='reservations')

    def __unicode__(self):
        return "%s from %s to %s (%s places)" % (self.subject.name, self.start, self.end, self.size)
