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

    @classmethod
    def reserve(cls, start, end, subject, owner):
        return cls.objects.create(start=start, end=end, subject=subject,
                                  owner=owner)
