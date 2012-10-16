from collections import defaultdict

from datetime import timedelta

from django.db.models import Q, Sum

from kitabu.search.utils import overlapping_reservations_Q, Timeline


class Subjects(object):

    def __init__(self, model, *args, **kwargs):
        self.subject_model = model
        self.reservation_model = model.get_reservation_model()

    def _get_subject_manager(self):
        if not hasattr(self, '_subject_manager'):
            self._subject_manager = self.subject_model.objects
        return self._subject_manager

    def _set_subject_manager(self, value):
        self._subject_manager = value

    subject_manager = property(_get_subject_manager, _set_subject_manager)


class ExclusivelyAvailableSubjects(Subjects):
    '''
    Form for searching subjects available in certain time period.
    Exclusive means only one reservation at a time is possible.
    '''

    def search(self, start, end):
        colliding_reservations = self.reservation_model.objects.filter(
            overlapping_reservations_Q(start, end),
            subject__in=self.subject_manager.all()
        )
        disqualified_subjects = colliding_reservations.values('subject_id') .distinct()
        return self.subject_manager.exclude(id__in=disqualified_subjects)


class SubjectsInCluster(Subjects):

    def __init__(self, subject_model, cluster_model, subject_related_name='subjects', *args, **kwargs):
        self.subject_model = subject_model
        self.reservation_model = subject_model.get_reservation_model()
        self.cluster_model = cluster_model
        self.subject_related_name = subject_related_name

    def _get_cluster_manager(self):
        if not hasattr(self, '_cluster_model_manager'):
            self._cluster_model_manager = self.cluster_model.objects
        return self._cluster_model_manager

    def _set_cluster_manager(self, value):
        self._cluster_model_manager = value

    cluster_manager = property(_get_cluster_manager, _set_cluster_manager)


class FiniteAvailability(Subjects):
    '''
    For searching subjects available in certain time period.
    Finite availablity means only certain number of reservations at a time is possible.
    '''

    def search(self, start, end, required_size):

        colliding_reservations = self.reservation_model.objects.filter(
            overlapping_reservations_Q(start, end),
            subject__in=self.subject_manager.all(),
        ).select_related('subject')

        timelines = defaultdict(lambda: defaultdict(lambda: 0))

        for reservation in colliding_reservations:
            reservation_start = max(start, reservation.start)
            timelines[reservation.subject][reservation_start] += reservation.size
            if reservation.end < end:
                timelines[reservation.subject][reservation.end] -= reservation.size

        disqualified_subjects = []
        for subject, timeline in timelines.iteritems():
            reservations_cnt = 0
            max_reservations = 0
            for moment in sorted(timeline.keys()):
                reservations_cnt += timeline[moment]
                if reservations_cnt > max_reservations:
                    max_reservations = reservations_cnt
                    if reservations_cnt + required_size > subject.size:
                        disqualified_subjects.append(subject.id)
                        break
        return self.subject_manager.exclude(id__in=disqualified_subjects, size__lt=required_size)


class FindPeriod(object):
    '''
    To search on certain subject for a period when it is available.
    E.g. to search for 7 days availability during May 2012.
    '''

    def search(self,
               start,
               end,
               required_duration=timedelta(1),
               subject=None,
               required_size=0,
               reservations=None
               ):
        timeline = Timeline(start, end, subject, reservations)

        available_size = subject.size if subject else 1
        if not required_size:
            required_size = available_size
        available_dates = []
        potential_start = timeline.start
        current_date = timeline.end
        current_size = 0

        for current_date, delta in timeline:
            current_size += delta
            if current_size + required_size <= available_size:
                if potential_start is None:
                    potential_start = current_date
            elif potential_start:
                if current_date - potential_start >= required_duration:
                    available_dates.append((potential_start, current_date))
                potential_start = None
        if (
            potential_start is not None
            and current_size + required_size <= available_size
            and end - potential_start >= required_duration
        ):
            available_dates.append((potential_start, end))
        return available_dates


class ClusterFiniteAvailability(SubjectsInCluster):
    '''
    Form for searching clusters available in certain time period.
    Finite availablity means only certain number of reservations at a time is possible.
    '''
    def search(self, start, end, required_size):

        clusters_with_size = self.cluster_manager.annotate(size=Sum(self.subject_related_name + '__size'))
        clusters_with_size_dict = dict((cluster.id, cluster) for cluster in clusters_with_size)

        colliding_reservations = self.reservation_model.objects.filter(
            overlapping_reservations_Q(start, end),
            subject__cluster_id__in=self.cluster_manager.all(),
        ).select_related('subject')

        timelines = defaultdict(lambda: defaultdict(lambda: 0))

        disqualified_clusters = []

        for reservation in colliding_reservations:
            reservation_start = start if reservation.start < start else reservation.start
            timelines[reservation.subject][reservation_start] += reservation.size
            if reservation.end < end:
                timelines[reservation.subject][reservation.end] -= reservation.size

        for subject, timeline in timelines.iteritems():
            reservations_cnt = 0
            max_reservations = 0
            for moment in sorted(timeline.keys()):
                reservations_cnt += timeline[moment]
                if reservations_cnt > max_reservations:
                    max_reservations = reservations_cnt

            cluster = clusters_with_size_dict[subject.cluster_id]
            cluster.size -= max_reservations
            if cluster.size < required_size:
                disqualified_clusters.append(subject.cluster_id)

        return clusters_with_size.filter(~Q(id__in=disqualified_clusters), size__gte=required_size)
