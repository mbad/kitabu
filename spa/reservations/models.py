from django.db import models
from django.contrib.auth.models import User
from reservable import ExclusiveReservable

class Reservable(models.Model, ExclusiveReservable):
    name = models.TextField(null=True, blank=True)

class Reservation(models.Model):
	reservable = models.ForeignKey('Reservable')
	start = models.DateTimeField()
	end = models.DateTimeField()