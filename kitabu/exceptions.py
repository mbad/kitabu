#-*- coding=utf-8 -*-


class SizeExceeded(Exception):
    pass


class OverlappingReservations(SizeExceeded):
    def __init__(self, reservations):
        self.reservations = reservations
