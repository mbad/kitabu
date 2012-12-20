# -*- coding: utf-8 -*-
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "spa.settings")

from lanes.models import Lane, LaneFullTimeValidator, LaneGivenHoursAndWeekdaysValidator
from pools.models import Pool
from django.contrib.auth.models import User


class DataLoader(object):
    def __init__(self):
        self.pools = {}
        self.validators = {}

    def load_all(self):
        self._load_pools()
        self._load_validators()
        self._load_users()
        self._load_lanes()

    def _load_pools(self):
        for pool_name in ['Konopnicka', 'Cygański', 'Aqua', 'Dmuchany przy domu', 'Olimpijski (Pekin)']:
            self.pools[pool_name] = Pool.objects.create(name=pool_name)

    def _load_validators(self):
        self.validators['Konopnicka'] = LaneFullTimeValidator.objects.create(interval=1, interval_type='hour')

        # Monday to Friday
        self.validators['Cygański'] = LaneGivenHoursAndWeekdaysValidator.create_from_bitlists(hours=[1] * 24,
                                                                                              days=[1, 1, 1, 1, 1, 0,
                                                                                                    0])

    def _load_lanes(self):
        for pool in self.pools.values():
            for i in range(1, 11):
                lane = Lane.objects.create(name="Tor {0}".format(i), cluster=pool, size=i + 10)
                if pool.name in self.validators:
                    lane.validators.add(self.validators[pool.name])

    def _load_users(self):
        for i in range(1, 6):
            User.objects.create(username="user{0}".format(i), password="haslo{0}".format(i), is_active=True,
                                first_name="Janusz {0}".format(i), last_name="Nowak {0}".format(i),
                                email="janusz.nowak{0}@example.com".format(i))


if __name__ == "__main__":
    try:
        pool = Pool.objects.get(name='Konopnicka')
    except Pool.DoesNotExist:
        loader = DataLoader()
        loader.load_all()
