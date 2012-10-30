#-*- coding=utf-8 -*-

from django.db import models


class BaseCluster(models.Model):
    class Meta:
        abstract = True

    name = models.TextField(null=True, blank=True)
