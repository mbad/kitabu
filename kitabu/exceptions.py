#-*- coding=utf-8 -*-


class ReservationError(Exception):
    ''' Error class to be thrown when reservation can't be made '''
    pass


class KitabuValidationError(ReservationError):
    ''' Error class to be thrown when a validator fails '''
    pass


class SizeExceeded(KitabuValidationError):
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


class OverlappingReservations(KitabuValidationError):
    def __init__(self, reservation, reservations):
        self.reservation = reservation
        self.reservations = reservations

        super(OverlappingReservations, self).__init__(
            u"Overlapping reservations for period %s-%s: %s" % (
                reservation.start, reservation.end, self.reservations))


class InvalidPeriod(KitabuValidationError):
    def __init__(self, message, reservation, validator):
        self.reservation = reservation
        self.validator = validator
        super(InvalidPeriod, self).__init__(
            message + u"(reservation: %s, validator: %s)" % (reservation, validator))


class TooManyReservations(KitabuValidationError):
    def __init__(self, reservation, validator, current):
        self.reservation = reservation
        self.validator = validator
        message = (u"Reached maximum number of reservations for user %(user)s %(on_subject)s(%(number)s)"
                   % {
                       'user': reservation.owner,
                       'on_subject': ('on subject %s' % reservation.subject) if current else '',
                       'number': (validator.max_reservations_on_current_subject
                                  if current else
                                  validator.max_reservations_on_all_subjects),
                   })
        super(TooManyReservations, self).__init__(message)
