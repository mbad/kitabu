from collections import defaultdict
from time import sleep

from django.db.models import Q
from django.db import transaction


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
        try:
            return super(EnsureSize, self).__getattribute__(name, *args)
        except AttributeError:
            if name == 'size':
                return 1
            else:
                raise


class AtomicReserver(object):
    @classmethod
    def non_transactional_reserve(cls, *args, **common_kwargs):
        reservations = []
        delay_time = common_kwargs.pop('delay_between_reservations', None)

        # explicitly lock these subjects before reserving them
        cls._lock_subjects(map(lambda t: t[0], args))

        for (subject, specific_kwargs) in args:
            reserve_kwargs = common_kwargs.copy()
            reserve_kwargs.update(specific_kwargs)
            reservation = subject.create_reservation(**reserve_kwargs)
            reservations.append(reservation)
            if delay_time is not None:
                sleep(delay_time)

        return reservations

    @classmethod
    @transaction.commit_manually
    def reserve(cls, *args, **kwargs):
        try:
            reservations = cls.non_transactional_reserve(*args, **kwargs)
            transaction.commit()
            return reservations
        except:
            transaction.rollback()
            raise

    @classmethod
    def _lock_subjects(cls, subjects):
        subjects_dict = defaultdict(lambda: [])
        for subject in subjects:
            subjects_dict[subject.__class__].append(subject.pk)

        for klass, pks in subjects_dict.iteritems():
            list(klass.objects.select_for_update().filter(pk__in=pks))
