from kitabu.subjects import VariableCapacitySubject
from kitabu.reservations import ReservationWithSize
from django.db import models
from pools.models import Pool


class Lane(VariableCapacitySubject):
    name = models.TextField()
    cluster = models.ForeignKey(Pool, related_name='subjects')

    def __unicode__(self):
        return self.name


class LaneReservation(ReservationWithSize):
    subject = models.ForeignKey('Lane', related_name='reservations')

    def __unicode__(self):
        return self.subject.name + ' - ' + str(self.size) + ' places'
