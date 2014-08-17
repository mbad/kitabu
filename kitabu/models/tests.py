#-*- coding=utf-8 -*-

from django.db import models


class IsolationTestSubject(models.Model):
    size = models.PositiveIntegerField()

    class Meta:
        app_label = 'kitabu'


class IsolationTestReservation(models.Model):
    subject = models.ForeignKey(IsolationTestSubject, related_name='reservations')
    size = models.PositiveIntegerField()

    class Meta:
        app_label = 'kitabu'
