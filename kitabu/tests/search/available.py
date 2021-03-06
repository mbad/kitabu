from datetime import datetime, timedelta

from django.test import TestCase

from kitabu.tests.models import Room, RoomReservation, Hotel, HotelRoom
from kitabu.search.available import FindPeriod, Clusters as ClustersSearcher, Subjects as SubjectsSearcher


class SearchAvailableSubject(TestCase):

    def setUp(self):
        self.room1 = Room.objects.create(name='Room 1', size=1)

    def test_find_subject_when_no_reservations_conflicting(self):
        RoomReservation.objects.create(
            subject=self.room1,
            size=1,
            start=datetime(2001, 1, 1),
            end=datetime(2001, 1, 8)
        )
        start = datetime(2000, 01, 01)
        end = datetime(2000, 01, 31)

        data = {
            'start': start,
            'end': end,
            'required_size': 1,
        }

        searcher = SubjectsSearcher(Room)

        self.assertEqual(1, len(searcher.search(**data)))

    def test_find_subject_when_no_reservations_at_all(self):
        RoomReservation.objects.all().delete()

        data = {
            'start': datetime(2000, 01, 01),
            'end': datetime(2000, 01, 31),
            'required_size': 1,
        }

        searcher = SubjectsSearcher(Room)

        self.assertEqual(1, len(searcher.search(**data)))

    def test_find_subject_when_no_reservations_at_all_and_not_enough_size(self):
        RoomReservation.objects.all().delete()

        data = {
            'start': datetime(2000, 01, 01),
            'end': datetime(2000, 01, 31),
            'required_size': 2,
        }

        searcher = SubjectsSearcher(Room)

        self.assertEqual(0, len(searcher.search(**data)))


class VaryingDateAndSizeSearchTest(TestCase):
    def setUp(self):
        '''
        For clean reading room1 has size of 1, room2 size of 2, and room3 - size 3.
        '''
        self.room1 = Room.objects.create(name='Room 1', size=1)
        self.room2 = Room.objects.create(name='Room 2', size=2)
        self.room3 = Room.objects.create(name='Room 3', size=3)

    def test_whole_period_available(self):
        RoomReservation.objects.create(
            subject=self.room1,
            size=1,
            start=datetime(2001, 1, 1),
            end=datetime(2001, 1, 8)
        )
        start = datetime(2000, 01, 01)
        end = datetime(2000, 01, 31)
        data = {
            'start': start,
            'end': end,
            'required_duration': timedelta(7),
            'required_size': 1,
            'subject': self.room1
        }
        searcher = FindPeriod()

        self.assertEqual(
            searcher.search(**data),
            [(start, end)]
        )

    def test_begin_of_period_unavailable(self):
        reservation = RoomReservation.objects.create(
            subject=self.room1,
            size=1,
            start=datetime(2001, 1, 1),
            end=datetime(2001, 1, 8)
        )
        start = datetime(2001, 01, 01)
        end = datetime(2001, 01, 31)
        data = {
            'start': start,
            'end': end,
            'required_duration': timedelta(7),
            'required_size': 1,
            'subject': self.room1,
        }
        searcher = FindPeriod()
        self.assertEqual(
            searcher.search(**data),
            [(reservation.end, end)]
        )

    def test_middle_of_period_unavailable(self):
        reservation = RoomReservation.objects.create(
            subject=self.room1,
            size=1,
            start=datetime(2001, 1, 1),
            end=datetime(2001, 1, 8)
        )
        start = datetime(2000, 12, 01)
        end = datetime(2001, 01, 31)
        data = {
            'start': start,
            'end': end,
            'required_duration': timedelta(7),
            'required_size': 1,
            'subject': self.room1,
        }
        searcher = FindPeriod()
        self.assertEqual(
            searcher.search(**data),
            [
                (start, reservation.start),
                (reservation.end, end)
            ]
        )

    def test_whole_period_available_but_with_concurrent_reservation(self):
        RoomReservation.objects.create(
            subject=self.room2,
            size=1,
            start=datetime(2001, 1, 1),
            end=datetime(2001, 1, 8)
        )
        start = datetime(2001, 01, 01)
        end = datetime(2001, 01, 31)
        data = {
            'start': start,
            'end': end,
            'required_duration': timedelta(7),
            'required_size': 1,
            'subject': self.room2,
        }
        searcher = FindPeriod()
        self.assertEqual(
            searcher.search(**data),
            [
                (start, end)
            ]
        )

    def test_middle_of_period_unavailable_one_place_missing(self):
        reservation = RoomReservation.objects.create(
            subject=self.room3,
            size=1,
            start=datetime(2001, 1, 8),
            end=datetime(2001, 1, 15)
        )  # this reservation will not collide as it has size one, leaving 2 places available

        reservation = RoomReservation.objects.create(
            subject=self.room3,
            size=2,
            start=datetime(2001, 1, 1),
            end=datetime(2001, 1, 8)
        )
        start = datetime(2000, 12, 01)
        end = datetime(2001, 01, 31)
        data = {
            'start': start,
            'end': end,
            'required_duration': timedelta(7),
            'required_size': 2,
            'subject': self.room3,
        }
        searcher = FindPeriod()
        self.assertEqual(
            searcher.search(**data),
            [
                (start, reservation.start),
                (reservation.end, end)
            ]
        )

    def test_period_unavailable(self):
        day = lambda day: datetime(2001, 1, day)
        reserve = lambda start, end, size: RoomReservation.objects.create(
            subject=self.room3,
            size=size,
            start=start,
            end=end
        )

        reserve(day(1), day(4), 3)
        reserve(day(4), day(7), 1)
        reserve(day(6), day(11), 1)
        reserve(day(8), day(15), 2)
        reserve(day(22), day(29), 2)

        start = datetime(2001, 01, 01)
        end = datetime(2001, 01, 31)
        data = {
            'start': start,
            'end': end,
            'required_duration': timedelta(8),
            'required_size': 2,
            'subject': self.room3
        }
        searcher = FindPeriod()
        self.assertEqual(
            searcher.search(**data),
            []
        )


class FindPeriodTestWithApprovableReservations(TestCase):
    def setUp(self):
        self.hotel = Hotel.objects.create(name='Hotel')
        self.room1 = HotelRoom.objects.create(name='Room 1', size=1, cluster=self.hotel)

    def test_begin_of_period_unavailable(self):
        reservation_start = datetime(2001, 1, 1)
        reservation_end = datetime(2001, 1, 8)

        preliminary_reservation_start = datetime(2001, 1, 8)
        preliminary_reservation_end = datetime(2001, 1, 14)

        invalid_preliminary_reservation_start = datetime(2001, 1, 14)
        invalid_preliminary_reservation_end = datetime(2001, 1, 20)

        self.room1.reserve(
            size=1,
            start=reservation_start,
            end=reservation_end
        )
        self.room1.reserve(
            size=1,
            start=preliminary_reservation_start,
            end=preliminary_reservation_end,
            valid_until=datetime(2100, 10, 10)
        )
        self.room1.reserve(
            size=1,
            start=invalid_preliminary_reservation_start,
            end=invalid_preliminary_reservation_end,
            valid_until=datetime(1900, 10, 10)
        )

        start = datetime(2001, 01, 01)
        end = datetime(2001, 01, 31)
        data = {
            'start': start,
            'end': end,
            'required_duration': timedelta(7),
            'required_size': 1,
            'subject': self.room1,
        }
        searcher = FindPeriod()
        self.assertEqual(
            searcher.search(**data),
            [(preliminary_reservation_end, end)]
        )


class ClusterFiniteAvailabilitySearchTest(TestCase):
    def setUp(self):
        '''
        All rooms in hotel1 have size of 5. Size of 10 in hotel2.
        '''
        self.hotel1 = Hotel.objects.create(name='Hotel 1')
        self.hotel2 = Hotel.objects.create(name='Hotel 2')

        self.room1 = HotelRoom.objects.create(name='Room 1', size=5, cluster=self.hotel1)
        self.room2 = HotelRoom.objects.create(name='Room 2', size=5, cluster=self.hotel1)
        self.room3 = HotelRoom.objects.create(name='Room 3', size=10, cluster=self.hotel2)
        self.room4 = HotelRoom.objects.create(name='Room 3', size=10, cluster=self.hotel2)

    def test_empty_clusters(self):
        start = datetime(2001, 01, 01)
        end = datetime(2001, 01, 31)
        data = {
            'start': start,
            'end': end,
            'required_size': 11,
        }
        searcher = ClustersSearcher(HotelRoom, Hotel, 'rooms')
        results = searcher.search(**data)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].name, 'Hotel 2')

    def test_all_reservations_overlapping(self):
        self.room1.reserve(start='2000-12-30', end='2001-01-22', size=1)
        self.room1.reserve(start='2000-11-30', end='2001-01-21', size=1)
        self.room2.reserve(start='2001-01-20', end='2001-02-11', size=2)

        self.room3.reserve(start='2001-01-05', end='2001-01-14', size=4)
        self.room3.reserve(start='2001-01-10', end='2001-01-17', size=4)
        self.room4.reserve(start='2000-12-20', end='2001-02-18', size=7)

        start = datetime(2001, 01, 01)
        end = datetime(2001, 01, 31)
        data = {
            'start': start,
            'end': end,
            'required_size': 6,
        }
        searcher = ClustersSearcher(HotelRoom, Hotel, 'rooms')
        results = searcher.search(**data)

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].name, 'Hotel 1')

    def test_the_need_to_switch_room(self):
        self.room3.reserve(start='2001-01-01', end='2001-01-15', size=5)
        self.room4.reserve(start='2001-01-01', end='2001-01-15', size=7)

        self.room3.reserve(start='2001-01-16', end='2001-01-25', size=7)
        self.room4.reserve(start='2001-01-16', end='2001-01-25', size=5)

        start = datetime(2001, 01, 01)
        end = datetime(2001, 01, 31)
        data = {
            'start': start,
            'end': end,
            'required_size': 7,
        }
        searcher = ClustersSearcher(HotelRoom, Hotel, 'rooms')

        results = searcher.search(**data)
        length = len(results)
        self.assertEqual(length, 1)
        self.assertEqual(results[0].name, 'Hotel 1')


class ClusterAvailabilityWithApprovableReservationsTest(TestCase):
    def setUp(self):
        '''
        All rooms in hotel1 have size of 5. Size of 10 in hotel2.
        '''
        self.hotel1 = Hotel.objects.create(name='Hotel 1')
        self.hotel2 = Hotel.objects.create(name='Hotel 2')

        self.room1 = HotelRoom.objects.create(name='Room 1', size=5, cluster=self.hotel1)
        self.room2 = HotelRoom.objects.create(name='Room 2', size=5, cluster=self.hotel1)
        self.room3 = HotelRoom.objects.create(name='Room 3', size=10, cluster=self.hotel2)
        self.room4 = HotelRoom.objects.create(name='Room 3', size=10, cluster=self.hotel2)

    def test_all_reservations_overlapping(self):
        # would fail if the second reservation was valid

        self.room1.reserve(start='2000-12-30', end='2001-01-22', size=1)
        self.room1.reserve(start='2000-11-30', end='2001-01-21', size=4, valid_until=datetime(1900, 10, 10))
        self.room2.reserve(start='2001-01-20', end='2001-02-11', size=2, valid_until=datetime(2100, 10, 10))

        reservation = self.room3.reserve(
            start='2001-01-05', end='2001-01-14', size=4, valid_until=datetime(1900, 10, 10))
        reservation.approve()
        self.room3.reserve(start='2001-01-10', end='2001-01-17', size=4)
        self.room4.reserve(start='2000-12-20', end='2001-02-18', size=7, valid_until=datetime(2100, 10, 10))

        start = datetime(2001, 01, 01)
        end = datetime(2001, 01, 31)
        data = {
            'start': start,
            'end': end,
            'required_size': 6,
        }
        searcher = ClustersSearcher(HotelRoom, Hotel, 'rooms')
        results = searcher.search(**data)

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].name, 'Hotel 1')
