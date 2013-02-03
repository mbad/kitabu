from django.db.models import Q


class ReservationSearch(object):
    def __init__(self, reservation_model):
        self.reservation_model = reservation_model

    def search(self, start, end, *args, **kwargs):
        return self.reservation_model.colliding_reservations(start=start, end=end, *args, **kwargs)


class SingleSubjectReservationSearch(ReservationSearch):
    def __init__(self, subject, *args, **kwargs):
        super(SingleSubjectReservationSearch, self).__init__(reservation_model=subject.reservation_model, *args,
                                                             **kwargs)
        self.subject = subject

    def search(self, *args, **kwargs):
        return super(SingleSubjectReservationSearch, self).search(subject=self.subject, *args, **kwargs)


class SingleSubjectManagerReservationSearch(ReservationSearch):
    def __init__(self, subject_manager, *args, **kwargs):
        super(SingleSubjectManagerReservationSearch, self).__init__(*args, **kwargs)
        self.subject_manager = subject_manager

    def search(self, *args, **kwargs):
        return super(SingleSubjectManagerReservationSearch, self).search(
            subject__in=self.subject_manager.all(), *args, **kwargs)
