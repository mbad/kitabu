from django.test import SimpleTestCase
from kitabu.tests.models import TennisCourt, Room, RoomReservation
from kitabu.exceptions import OverlappingReservations, SizeExceeded, AtomicReserveError


class TennisCourtTest(SimpleTestCase):
    def setUp(self):
        self.court = TennisCourt.objects.create(name="court")

    def test_one_reservation(self):
        self.court.reserve('2012-04-01', '2012-05-11')
        self.assertEqual(self.court.reservations.count(), 1, "Should have one reservation")

    def test_two_non_overlapping_reservations(self):
        self.court.reserve('2012-04-01 12:00', '2012-05-11 12:00')
        self.court.reserve('2012-05-11 12:00', '2012-05-15 12:00')
        self.assertEqual(self.court.reservations.count(), 2, "Should have two reservations")

    def test_two_overlappping_reservations(self):
        with self.assertRaises(OverlappingReservations):
            self.court.reserve('2012-04-01', '2012-05-11')
            self.court.reserve('2012-04-20', '2012-05-15')

    def test_two_minimally_overlappping_reservations(self):
        with self.assertRaises(OverlappingReservations):
            self.court.reserve('2012-04-01', '2012-05-11 12:00')
            self.court.reserve('2012-05-11 11:59:59', '2012-05-15')


class RoomTest(SimpleTestCase):
    def setUp(self):
        self.room = Room.objects.create(name="room", size=5)

    def test_one_reservation(self):
        self.room.reserve('2012-04-01', '2012-05-11', 3)
        self.assertEqual(self.room.reservations.count(), 1, "Should have one reservation")
        self.assertEqual(self.room.reservations.get().size, 3, "Should have 3 places reserved")

    def test_two_overlapping_reservation_with_size_not_exceeded(self):
        self.room.reserve('2012-04-01', '2012-05-11', 3)
        self.room.reserve('2012-04-15', '2012-05-13', 2)
        self.assertEqual(self.room.reservations.count(), 2, "Should have two reservations")
        reservations = self.room.reservations.all()
        sum = reduce(lambda s, r: s + r.size, reservations, 0)
        self.assertEqual(sum, 5, "Should have 5 places reserved")

    def test_two_overlapping_reservation_with_size_exceeded(self):
        with self.assertRaises(SizeExceeded):
            self.room.reserve('2012-04-01', '2012-05-11', 3)
            self.room.reserve('2012-04-15', '2012-05-13', 3)


class AtomicReserveTest(SimpleTestCase):
    def setUp(self):
        self.room5 = Room.objects.create(name="room", size=5)
        self.room1 = Room.objects.create(name="room", size=1)
        self.room3 = Room.objects.create(name="room", size=3)

    def test_proper_atomic_reservation(self):
        initial_count = RoomReservation.objects.count()
        reservations = Room.objects.atomic_reserve(
                                                   (self.room5, {'start': '2012-04-01', 'end': '2012-05-12',
                                                                 'size': 3}),
                                                   (self.room1, {'start': '2012-04-01', 'end': '2012-05-12',
                                                                 'size': 1}),
                                                   (self.room3, {'start': '2012-04-01', 'end': '2012-05-12',
                                                                 'size': 2})
                                                   )
        self.assertEqual(len(reservations), 3, 'There should be 3 reservation objects returned')
        self.assertEqual(reservations[0].size, 3, 'First reservation should have size equal to 3')
        self.assertEqual(RoomReservation.objects.count(), initial_count + 3,
                         'There should be 3 reservation objects added to the database')

    def test_unproper_atomic_reservation(self):
        initial_count = RoomReservation.objects.count()
        with self.assertRaises(AtomicReserveError):
            Room.objects.atomic_reserve(
                                        (self.room5, {'start': '2012-04-01', 'end': '2012-05-12', 'size': 3}),
                                        (self.room1, {'start': '2012-04-01', 'end': '2012-05-12', 'size': 1}),
                                        (self.room3, {'start': '2012-04-01', 'end': '2012-05-12', 'size': 5})
                                        )
        self.assertEqual(RoomReservation.objects.count(), initial_count,
                         'There should be no reservation objects added to the database')
