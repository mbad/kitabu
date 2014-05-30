#-*- coding: utf-8 -*-

from django.core.management.base import BaseCommand, CommandError
from lanes.models import Lane
from pools.models import Pool
from django.contrib.auth.models import User


class Command(BaseCommand):
    help = 'Loads initial data for kitabu'

    def handle(self, *args, **options):
        DataLoader().load_all()


class DataLoader(object):
    def __init__(self):
        self.pools = {}

    def load_all(self):
        self._load_pools()
        self._load_lanes()

    def _load_pools(self):
        for pool_name in ['Konopnicka', 'Cygański', 'Aqua', 'Dmuchany przy domu', 'Olimpijski (Pekin)']:
            try:
                pool = Pool.objects.get(name=pool_name)
                pool.delete()
            except Pool.DoesNotExist:
                pass
            self.pools[pool_name] = Pool.objects.create(name=pool_name)

    def _load_lanes(self):
        for pool in self.pools.values():
            for i in range(1, 11):
                Lane.objects.create(name="Tor {0} - {1}".format(i, pool.name), cluster=pool, size=i + 10)
