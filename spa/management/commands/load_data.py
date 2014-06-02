#-*- coding: utf-8 -*-

from django.core.management.base import BaseCommand
from lanes.models import Lane, LaneFullTimeValidator
from pools.models import Pool


class Command(BaseCommand):
    help = 'Loades initial data for kitabu'

    def handle(self, *args, **options):
        DataLoader().load_all()


class DataLoader(object):
    def __init__(self):
        self.pools = {}
        self.validators = {}

    def load_all(self):
        self._load_pools()
        self._load_validators()
        self._load_lanes()

    def _load_pools(self):
        for pool_name in ['Konopnicka', 'Cygański', 'Aqua', 'Dmuchany przy domu', 'Olimpijski (Pekin)']:
            try:
                pool = Pool.objects.get(name=pool_name)
                for lane in pool.lanes.all():
                    lane.validators.all().delete()
                pool.delete()
            except Pool.DoesNotExist:
                pass
            self.pools[pool_name] = Pool.objects.create(name=pool_name)

    def _load_validators(self):
        self.validators['Konopnicka'] = LaneFullTimeValidator.objects.create(interval=1, interval_type='hour')

    def _load_lanes(self):
        for pool in self.pools.values():
            for i in range(1, 11):
                lane = Lane.objects.create(name="Tor {0} - {1}".format(i, pool.name), cluster=pool, size=i + 10)
                if pool.name in self.validators:
                    lane.validators.add(self.validators[pool.name])
