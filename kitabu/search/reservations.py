# TODO: This module might use a little refactoring. Espacially passing *args
# and use of __init__ could use a closer look.


class ReservationSearch(object):
    """Searcher for reservations.

    Constructor takes reservation model.
    ``search`` method on intialized object takes start and end arguments,
    plus any narrowing search criteria.
    """
    def __init__(self, reservation_model):
        self.reservation_model = reservation_model

    def search(self, start, end, *args, **kwargs):
        return self.reservation_model.colliding_reservations(start=start, end=end, *args, **kwargs)


class SingleSubjectReservationSearch(ReservationSearch):
    """Searcher to find all reservations on given subject."""
    def __init__(self, subject, *args, **kwargs):
        super(SingleSubjectReservationSearch, self).__init__(reservation_model=subject.reservation_model, *args,
                                                             **kwargs)
        self.subject = subject

    def search(self, *args, **kwargs):
        return super(SingleSubjectReservationSearch, self).search(subject=self.subject, *args, **kwargs)


class SingleSubjectManagerReservationSearch(ReservationSearch):
    """Searcher for reservation on given subjects set (manager).

    Easily used to search on for reservations e.g. on a cluster.

    """

    def __init__(self, subject_manager, *args, **kwargs):
        super(SingleSubjectManagerReservationSearch, self).__init__(*args, **kwargs)
        self.subject_manager = subject_manager

    def search(self, *args, **kwargs):
        return super(SingleSubjectManagerReservationSearch, self).search(
            subject__in=self.subject_manager.all(), *args, **kwargs)
