#-*- coding: utf-8 -*-

from django.core.management.base import BaseCommand
from django.db import transaction
from kitabu.models.tests import IsolationTestSubject, IsolationTestReservation
from threading import Thread
from time import sleep

DELAY = 0.2
INITIAL_DELAY = 0.1


class Command(BaseCommand):
    help = 'Tests kitabu security'

    def handle(self, *args, **options):
        self.clean()
        self.prepare_db()
        if self.check_isolation():
            print 'OK! Reservations are secure.'
        else:
            print 'WARNING! Reservations are not secure. Check your transaction isolation settings.'
        self.clean()

    def clean(self):
        IsolationTestReservation.objects.all().delete()
        IsolationTestSubject.objects.all().delete()

    def prepare_db(self):
        self.subject = IsolationTestSubject.objects.create(size=10)
        self.subject.reservations.create(size=5)

    def check_isolation(self):
        threads = [Thread(target=self.create_reservation), Thread(target=self.create_reservation, args=(INITIAL_DELAY,))]
        [t.start() for t in threads]
        [t.join() for t in threads]
        return IsolationTestReservation.objects.count() == 2

    def create_reservation(self, initial_delay=0):
        sleep(initial_delay)
        with transaction.commit_manually():
            sleep(DELAY)
            list(IsolationTestSubject.objects.select_for_update().filter(pk=self.subject.pk))
            sleep(DELAY)
            reservations = list(IsolationTestReservation.objects.filter(subject=self.subject))
            sleep(DELAY)
            if reduce(lambda acc, r: acc + r.size, reservations, 0) + 4 <= self.subject.size:
                IsolationTestReservation.objects.create(size=4, subject=self.subject)
            sleep(DELAY)
            transaction.commit()
