from django.db import models
from kitabu.subjects import ExclusiveSubject
from kitabu.reservations import BaseReservation


class Subject(ExclusiveSubject):
    name = models.TextField(null=True, blank=True)


class Reservation(BaseReservation):
    pass
