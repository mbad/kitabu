#from django.db import models
#from django.contrib.auth.models import User
#
#
#class Reservable(object):
#    name = models.TextField(null=True, blank=True)
#    owner = models.ForeignKey(User)
#    reservable_group = models.ForeignKey('ReservableGroup', null=True)
#
#
#class ReservableGroup(object):
#    name = models.TextField(null=True, blank=True)
#    owner = models.ForeignKey(User)
#
#
#class Reservation(object):
#    owner = models.ForeignKey(User, null=True)
#    reservable = models.ForeignKey('Reservable')
#    start = models.DateTimeField()
#    end = models.DateTimeField()
