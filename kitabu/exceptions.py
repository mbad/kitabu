#-*- coding=utf-8 -*-


class ReservationError(Exception):
    ''' Error class to be thrown when reservation can't be made '''
    pass


class SizeExceeded(ReservationError):
    def __init__(self, message="Too many reservations"):
        super(SizeExceeded, self).__init__(message)


class ValidationError(ReservationError):
    ''' Error class to be thrown when a validator fails '''
    pass
