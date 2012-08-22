#-*- coding=utf-8 -*-


class CapacityExceeded(Exception):
    pass


class OverlappingReservations(CapacityExceeded):
    def __init__(self, reservations):
        self.reservations = reservations
