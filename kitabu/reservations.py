#-*- coding=utf-8 -*-

from django.db import models
from django.contrib.auth.models import User


class BaseReservation(models.Model):
    class Meta:
        abstract = True

    owner = models.ForeignKey(User, null=True)
    subject = models.ForeignKey('Subject')
    start = models.DateTimeField()
    end = models.DateTimeField()
