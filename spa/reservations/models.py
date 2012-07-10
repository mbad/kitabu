from django.db import models
from reservable import ExclusiveReservable

class Reservable(ExclusiveReservable):
    class Meta:
        app_label = 'reservations'
    name = models.TextField(null=True, blank=True)

class Reservation(models.Model):
	reservable = models.ForeignKey('Reservable')
	start = models.DateTimeField()
	end = models.DateTimeField()
