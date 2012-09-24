#-*- coding=utf-8 -*-

from django.db import models, transaction
from kitabu.exceptions import AtomicReserveError


class SubjectManager(models.Manager):
    @transaction.commit_manually
    def atomic_reserve(self, *args):
        reservations = []

        for (subject, kwargs) in args:
            try:
                reservation = subject.reserve(**kwargs)
                reservations.append(reservation)
            except:
                transaction.rollback()
                raise AtomicReserveError

        transaction.commit()
        return reservations
