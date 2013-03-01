#-*- coding=utf-8 -*-


class ReservationError(Exception):
    ''' Error class to be thrown when a validator fails '''
    pass


class SizeExceeded(ReservationError):
    def __init__(self, subject, requested_size, start, end, overlapping_reservations=None):
        self.subject = subject
        self.requested_size = requested_size
        self.start = start
        self.end = end
        self.overlapping_reservations = overlapping_reservations
        msg = (u"for reservation on subject %(subject)s of size %(subject_size)s "
               "for period %(start)s-%(end)s (requested size: %(requested_size)s)" % {
                   'subject': subject,
                   'subject_size': subject.size,
                   'start': start,
                   'end': end,
                   'requested_size': requested_size,
               })
        if overlapping_reservations:
            msg += "(colliding reservations: %s)" % overlapping_reservations

        super(SizeExceeded, self).__init__(msg)


class OverlappingReservations(ReservationError):
    def __init__(self, reservation, reservations):
        self.reservation = reservation
        self.reservations = reservations

        super(OverlappingReservations, self).__init__(
            u"Overlapping reservations for period %s-%s: %s" % (
                reservation.start, reservation.end, self.reservations))


class ValidatorError(ReservationError):
    pass


class InvalidPeriod(ValidatorError):
    def __init__(self, *a, **ka):
        pass


class TimeUnitNotNull(InvalidPeriod):
    def __init__(self, unit):
        self.unit = unit


class TimeUnitNotDivisible(InvalidPeriod):
    def __init__(self, time_unit, interval):
        self.unit = time_unit
        self.interval = interval


class TooSoon(InvalidPeriod):
    def __init__(self, expected_period):
        self.expected_period = expected_period


class TooLate(InvalidPeriod):
    def __init__(self, expected_period):
        self.expected_period = expected_period


class OutsideAllowedPeriods(InvalidPeriod):
    def __init__(self, periods):
        self.periods = periods


class ForbiddenPeriod(InvalidPeriod):
    def __init__(self, start, end):
        self.start = start
        self.end = end


class ForbiddenHours(InvalidPeriod):
    def __init__(self, schedule):
        self.schedule = schedule


class TooLong(InvalidPeriod):
    def __init__(self, max_allowed_seconds):
        self.max_allowed_seconds = max_allowed_seconds


class TooManyReservations(ValidatorError):
    pass


class TooManyReservationsForUser(TooManyReservations):
    def __init__(self, max_allowed):
        self.max_allowed = max_allowed


class TooManyReservationsOnSubjectForUser(TooManyReservations):
    def __init__(self, max_allowed):
        self.max_allowed = max_allowed
