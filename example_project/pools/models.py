#-*- coding=utf-8 -*-

from kitabu.models.clusters import BaseCluster


class Pool(BaseCluster):
    def __unicode__(self):
        return self.name

    @property
    def lanes(self):
        return self.subjects
