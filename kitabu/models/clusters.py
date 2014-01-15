#-*- coding=utf-8 -*-

from django.db import models


class BaseCluster(models.Model):
    """Cluster to group subjects of reservations.

    This is used to logically bind together subjects that somehow belong
    together. Some examples could a pool that gathers lanes, a hotel that
    gathers rooms, or a coffe shop that gathers specific tables.

    This class on its own provides no functionality.
    TODO: add references of what uses the class.

    When subclassing this class, remember to add foreign key to it
    in your **Subject** subclass:

        cluster = models.ForeignKey(YourBaseClusterSubclass)

    """
    class Meta:
        abstract = True

    name = models.TextField(blank=True)
