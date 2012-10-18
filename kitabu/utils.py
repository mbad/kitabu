from collections import defaultdict

from django.db.models import Q
from django.db import transaction
from kitabu.exceptions import AtomicReserveError


class Timeline(list):
    def __init__(self, subject, start, end):
        self.start = start
        self.end = end
        self.subject = subject

        colliding_reservations = subject.reservation_model.objects.filter(
            (
                Q(start__gte=start, start__lt=end)   # start in scope
                | Q(end__gt=start, end__lte=end)     # end in scope
                | Q(start__lte=start, end__gte=end)  # covers whole scope
            ),
            subject=subject,
        ).select_related('subject')

        timeline = defaultdict(lambda: 0)

        for reservation in colliding_reservations:
            reservation_start = start if reservation.start < start else reservation.start
            timeline[reservation_start] += reservation.size

            timeline[min(reservation.end, end)] -= reservation.size

        return super(Timeline, self).__init__(sorted(timeline.iteritems()))


class EnsureSize(object):
    def __getattribute__(self, name, *args):
        if name != 'size':
            return super(EnsureSize, self).__getattribute__(name, *args)
        try:
            return super(EnsureSize, self).__getattribute__(name, *args)
        except AttributeError:
            return 1


class AtomicReserver(object):
    @classmethod
    def _non_transactional_reserve(cls, *args, **common_kwargs):
        reservations = []
        try:
            for (subject, specific_kwargs) in args:
                reserve_kwargs = common_kwargs.copy()
                reserve_kwargs.update(specific_kwargs)
                reservation = subject.reserve(**reserve_kwargs)
                reservations.append(reservation)

            return reservations
        except:
            raise AtomicReserveError

    @classmethod
    @transaction.commit_manually
    def reserve(cls, *args, **kwargs):
        reservations = []
        try:
            reservations = cls._non_transactional_reserve(*args, **kwargs)
            transaction.commit()
            return reservations
        except AtomicReserveError:
            transaction.rollback()
            raise
