from collections import defaultdict

from django.db.models import Q


class Timeline(list):
    def __init__(self, start, end, subject=None, reservations=None):
        assert any([subject, reservations]), "You must provide either subject or reservations"
        self.start = start
        self.end = end
        self.subject = subject

        if subject and not reservations:
            reservations = subject.reservation_model.objects.filter(
                (
                    Q(start__gte=start, start__lt=end)   # start in scope
                    | Q(end__gt=start, end__lte=end)     # end in scope
                    | Q(start__lte=start, end__gte=end)  # covers whole scope
                ),
                subject=subject,
            ).select_related('subject')
        elif subject and reservations:
            reservations = [r for r in reservations if r.subject_id == subject.id]

        timeline = defaultdict(lambda: 0)

        for reservation in reservations:
            timeline[max(start, reservation.start)] += reservation.size
            timeline[min(reservation.end, end)] -= reservation.size

        super(Timeline, self).__init__(sorted(timeline.iteritems()))

    def max(self):
        current_max = current = 0
        for date, delta in self:
            current += delta
            current_max = max(current, current_max)

        return current_max
