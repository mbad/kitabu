#-*- coding: utf-8 -*-

from datetime import datetime

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

from lanes.models import (
    Lane,
    LFullTimeValidator,
    LTimeIntervalValidator,
    LWithinPeriodValidator,
    Period,
    LNotWithinPeriodValidator,
    LMaxReservationsPerUserValidator,
)
from pools.models import Pool


class Command(BaseCommand):
    help = 'Loades initial data for kitabu v0.5'

    def handle(self, *args, **options):
        DataLoader().load_all()


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
            try:
                pool = Pool.objects.get(name=pool_name)
                for lane in pool.lanes.all():
                    lane.validators.all().delete()
                pool.delete()
            except Pool.DoesNotExist:
                pass
            self.pools[pool_name] = Pool.objects.create(name=pool_name)

    def _load_validators(self):
        self.validators['Konopnicka'] = LFullTimeValidator.objects.create(interval=1, interval_type='hour')

        LTimeIntervalValidator.objects.create(
            time_value='30', time_unit='minute', interval_type='s', apply_to_all=True)
        v = LWithinPeriodValidator.objects.create(apply_to_all=True)
        Period.objects.create(validator=v, start=datetime(2013, 1, 1), end=datetime(2015, 12, 31))
        LNotWithinPeriodValidator.objects.create(
            start=datetime(2014, 7, 1), end=datetime(2014, 8, 31), apply_to_all=True)
        LMaxReservationsPerUserValidator.objects.create(
            max_reservations_on_all_subjects=10, max_reservations_on_current_subject=3, apply_to_all=True)

    def _load_lanes(self):
        for pool in self.pools.values():
            for i in range(1, 11):
                lane = Lane.objects.create(name="Tor {0} - {1}".format(i, pool.name), cluster=pool, size=i + 10)
                if pool.name in self.validators:
                    lane.validators.add(self.validators[pool.name])

    def _load_users(self):
        for i in range(1, 6):
            email = "janusz.nowak{0}@example.com".format(i)
            try:
                User.objects.get(email=email).delete()
            except User.DoesNotExist:
                pass
            user = User.objects.create(
                username="user{0}".format(i),
                is_active=True,
                first_name="Janusz {0}".format(i),
                last_name="Nowak {0}".format(i),
                email=email)
            user.set_password("haslo{0}".format(i))
            user.save()
