import settings

from django.test import SimpleTestCase
from models import TennisCourt, Room
from kitabu.exceptions import OverlappingReservations, SizeExceeded


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
        sum = reduce(lambda r1, r2: r1.size + r2.size, reservations)
        self.assertEqual(sum, 5, "Should have 5 places reserved")

    def test_two_overlapping_reservation_with_size_exceeded(self):
        with self.assertRaises(SizeExceeded):
            self.room.reserve('2012-04-01', '2012-05-11', 3)
            self.room.reserve('2012-04-15', '2012-05-13', 3)
