#-*- coding=utf-8 -*-

from django.db import models
from django.contrib.auth.models import User


class BaseReservation(models.Model):
    class Meta:
        abstract = True

    owner = models.ForeignKey(User, null=True)
    start = models.DateTimeField()
    end = models.DateTimeField()

    @classmethod
    def reserve(cls, start, end, subject, owner, **kwargs):
        return cls.objects.create(start=start, end=end, subject=subject,
                                  owner=owner, **kwargs)


class ReservationWithSize(BaseReservation):
    class Meta:
        abstract = True
        
    size = models.IntegerField()
    
    @classmethod
    def reserve(cls, start, end, subject, owner, desired_reservations_nr, **kwargs):
        return super(ReservationWithSize, cls).reserve(start, end, subject, owner, 
                                                       size=desired_reservations_nr, **kwargs)
