#-*- coding=utf-8 -*-

from django.db import models
from django.contrib.auth.models import User


class BaseCluster(models.Model):
    class Meta:
        abstract = True

    name = models.TextField(null=True, blank=True)


class OwnedCluster(BaseCluster):
    class Meta:
        abstract = True

    owner = models.ForeignKey(User)
