from django.test import TestCase

from kitabu.tests.models import (
    Hotel,
    HotelRoom,
    HotelRoomReservation,
    RoomWithApprovableReservations,
    ApprovableRoomReservation
)
from kitabu.search.reservations import (
    ReservationSearch,
    SingleSubjectReservationSearch,
    SingleSubjectManagerReservationSearch
)


class ReservationSearchTest(TestCase):
    def setUp(self):
        self.hotel1 = Hotel.objects.create(name='Hotel 1')
        self.hotel2 = Hotel.objects.create(name='Hotel 2')

        self.room1 = HotelRoom.objects.create(name='Room 1', size=50, cluster=self.hotel1)
        self.room2 = HotelRoom.objects.create(name='Room 2', size=50, cluster=self.hotel2)

        self.room1.reserve(start='2001-01-01', end='2001-01-15', size=5)
        self.room1.reserve(start='2001-01-10', end='2001-01-25', size=5)
        self.room1.reserve(start='2001-02-12', end='2001-02-20', size=5)

        self.room2.reserve(start='2001-01-01', end='2001-01-15', size=5)
        self.room2.reserve(start='2001-01-10', end='2001-01-25', size=5)
        self.room2.reserve(start='2001-02-12', end='2001-02-20', size=5)

    def test_search_in_all_reservations(self):
        results = ReservationSearch(reservation_model=HotelRoomReservation).search('2001-01-05', '2001-01-22')
        length = len(results)
        self.assertEqual(length, 4, 'There should be 4 results returned')

    def test_search_in_one_subject(self):
        results = SingleSubjectReservationSearch(subject=self.room1).search('2001-01-05', '2001-01-22')
        length = len(results)
        self.assertEqual(length, 2, 'There should be 2 results returned')

    def test_search_in_one_cluster(self):
        search = SingleSubjectManagerReservationSearch(subject_manager=self.hotel1.rooms,
                                                       reservation_model=HotelRoomReservation)
        results = search.search('2001-01-05', '2001-01-22')
        length = len(results)
        self.assertEqual(length, 2, 'There should be 2 results returned')


class ApprovableReservationSearchTest(TestCase):
    def setUp(self):
        self.hotel1 = Hotel.objects.create(name='Hotel 1')
        self.hotel2 = Hotel.objects.create(name='Hotel 2')

        self.room1 = HotelRoom.objects.create(name='Room 1', size=50, cluster=self.hotel1)
        self.room2 = HotelRoom.objects.create(name='Room 2', size=50, cluster=self.hotel2)

        self.room1.make_preliminary_reservation(start='2050-01-01', end='2050-01-15', size=5, valid_until='2100-10-10')
        self.room1.make_preliminary_reservation(start='2050-01-10', end='2050-01-25', size=5, valid_until='1900-10-10')
        self.room1.make_preliminary_reservation(start='2050-02-12', end='2050-02-20', size=5, valid_until='2100-10-10')

        self.room2.make_preliminary_reservation(start='2050-01-01', end='2050-01-15', size=5, valid_until='1900-10-10')
        self.room2.make_preliminary_reservation(start='2050-01-10', end='2050-01-25', size=5, valid_until='2100-10-10')
        self.room2.make_preliminary_reservation(start='2050-02-12', end='2050-02-20', size=5, valid_until='2100-10-10')

    def test_search_in_all_reservations(self):
        results = ReservationSearch(reservation_model=HotelRoomReservation).search('2050-01-05', '2050-01-22')
        length = len(results)
        self.assertEqual(length, 2, 'There should be 2 results returned')

    def test_search_in_one_subject(self):
        results = SingleSubjectReservationSearch(subject=self.room1).search('2050-01-05', '2050-01-22')
        length = len(results)
        self.assertEqual(length, 1, 'There should be 1 result returned')

    def test_search_in_one_cluster(self):
        search = SingleSubjectManagerReservationSearch(subject_manager=self.hotel1.rooms,
                                                       reservation_model=HotelRoomReservation)
        results = search.search('2050-01-05', '2050-01-22')
        length = len(results)
        self.assertEqual(length, 1, 'There should be 1 results returned')
