from django.db import models
from django.contrib.auth.models import User


class Reservable(models.Model):
    name = models.TextField(null=True, blank=True)
    owner = models.ForeignKey(User)
    reservable_group = models.ForeignKey('ReservableGroup', null=True)


class ReservableGroup(models.Model):
    name = models.TextField(null=True, blank=True)
    owner = models.ForeignKey(User)


class Reservation(models.Model):
    owner = models.ForeignKey(User, null=True)
    reservable = models.ForeignKey('Reservable') 
    start = models.DateTimeField()
    end = models.DateTimeField()



