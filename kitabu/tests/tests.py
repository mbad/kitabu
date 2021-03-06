from datetime import datetime
from mock import patch
from threading import Thread
from time import sleep

from django.test import TransactionTestCase, TestCase

from kitabu.tests.models import (
    TennisCourt,
    Room,
    OtherRoom,
    RoomReservation,
    OtherRoomReservation,
    TestReservationGroup,
    FiveSeatsBus,
    ConferenceRoom,
    ConferenceRoomReservation,
    RoomWithApprovableReservations,
    ApprovableRoomReservation
)
from kitabu.exceptions import (
    SizeExceeded,
    ReservationError,
    OverlappingReservations,
    OutdatedReservationError,
)
from kitabu.utils import AtomicReserver


class TennisCourtTest(TestCase):
    def setUp(self):
        self.court = TennisCourt.objects.create(name="court")

    def test_one_reservation(self):
        self.court.reserve(start='2012-04-01', end='2012-05-11')
        self.assertEqual(self.court.reservations.count(), 1, "Should have one reservation")

    def test_two_non_overlapping_reservations(self):
        self.court.reserve(start='2012-04-01 12:00', end='2012-05-11 12:00')
        self.court.reserve(start='2012-05-11 12:00', end='2012-05-15 12:00')
        self.assertEqual(self.court.reservations.count(), 2, "Should have two reservations")

    def test_two_overlappping_reservations(self):
        with self.assertRaises(OverlappingReservations):
            self.court.reserve(start='2012-04-01', end='2012-05-11')
            self.court.reserve(start='2012-04-20', end='2012-05-15')

    def test_two_minimally_overlappping_reservations(self):
        with self.assertRaises(OverlappingReservations):
            self.court.reserve(start='2012-04-01', end='2012-05-11 12:00')
            self.court.reserve(start='2012-05-11 11:59:59', end='2012-05-15')


class RoomTest(TestCase):
    def setUp(self):
        self.room = Room.objects.create(name="room", size=5)

    def test_one_reservation(self):
        self.room.reserve(start='2012-04-01', end='2012-05-11', size=3)
        self.assertEqual(self.room.reservations.count(), 1, "Should have one reservation")
        self.assertEqual(self.room.reservations.get().size, 3, "Should have 3 places reserved")

    def test_two_overlapping_reservation_with_size_not_exceeded(self):
        self.room.reserve(start='2012-04-01', end='2012-05-11', size=3)
        self.room.reserve(start='2012-04-15', end='2012-05-13', size=2)
        self.assertEqual(self.room.reservations.count(), 2, "Should have two reservations")
        reservations = self.room.reservations.all()
        sum = reduce(lambda s, r: s + r.size, reservations, 0)
        self.assertEqual(sum, 5, "Should have 5 places reserved")

    def test_two_overlapping_reservation_with_size_exceeded(self):
        with self.assertRaises(SizeExceeded):
            self.room.reserve(start='2012-04-01', end='2012-05-11', size=3)
            self.room.reserve(start='2012-04-15', end='2012-05-13', size=3)


class BusTest(TestCase):
    def setUp(self):
        self.bus = FiveSeatsBus.objects.create(name="bus")

    def test_one_reservation(self):
        self.bus.reserve(start='2012-04-01', end='2012-05-11', size=3)
        self.assertEqual(self.bus.reservations.count(), 1, "Should have one reservation")
        self.assertEqual(self.bus.reservations.get().size, 3, "Should have 3 places reserved")

    def test_two_overlapping_reservation_with_size_not_exceeded(self):
        self.bus.reserve(start='2012-04-01', end='2012-05-11', size=3)
        self.bus.reserve(start='2012-04-15', end='2012-05-13', size=2)
        self.assertEqual(self.bus.reservations.count(), 2, "Should have two reservations")
        reservations = self.bus.reservations.all()
        sum = reduce(lambda s, r: s + r.size, reservations, 0)
        self.assertEqual(sum, 5, "Should have 5 places reserved")

    def test_two_overlapping_reservation_with_size_exceeded(self):
        with self.assertRaises(SizeExceeded):
            self.bus.reserve(start='2012-04-01', end='2012-05-11', size=3)
            self.bus.reserve(start='2012-04-15', end='2012-05-13', size=3)


class AtomicReserveTest(TransactionTestCase):
    def setUp(self):
        self.room5 = Room.objects.create(name="room", size=5)
        self.room1 = Room.objects.create(name="room", size=1)
        self.room3 = Room.objects.create(name="room", size=3)

    def test_proper_atomic_reservation(self):
        initial_count = RoomReservation.objects.count()
        reservations = AtomicReserver.reserve(
            (self.room5, {'start': '2012-04-01', 'end': '2012-05-12', 'size': 3}),
            (self.room1, {'start': '2012-04-01', 'end': '2012-05-12', 'size': 1}),
            (self.room3, {'start': '2012-04-01', 'end': '2012-05-12', 'size': 2})
        )
        self.assertEqual(len(reservations), 3, 'There should be 3 reservation objects returned')
        self.assertEqual(reservations[0].size, 3, 'First reservation should have size equal to 3')
        self.assertEqual(RoomReservation.objects.count(), initial_count + 3,
                         'There should be 3 reservation objects added to the database')

    def test_improper_atomic_reservation(self):
        initial_count = RoomReservation.objects.count()
        with self.assertRaises(ReservationError):
            AtomicReserver.reserve(
                (self.room5, {'start': '2012-04-01', 'end': '2012-05-12', 'size': 3}),
                (self.room1, {'start': '2012-04-01', 'end': '2012-05-12', 'size': 1}),
                (self.room3, {'start': '2012-04-01', 'end': '2012-05-12', 'size': 5})
            )
        self.assertEqual(RoomReservation.objects.count(), initial_count,
                         'There should be no reservation objects added to the database')


class GroupReservationTest(TransactionTestCase):
    def setUp(self):
        self.room5 = Room.objects.create(name="room", size=5)
        self.room1 = Room.objects.create(name="room", size=1)
        self.room3 = Room.objects.create(name="room", size=3)

    def test_proper_group_reservation(self):
        initial_reservation_count = RoomReservation.objects.count()
        initial_group_count = TestReservationGroup.objects.count()

        group = TestReservationGroup.reserve(
            (self.room5, {'start': '2012-04-01', 'end': '2012-05-12', 'size': 3}),
            (self.room1, {'start': '2012-04-01', 'end': '2012-05-12', 'size': 1}),
            (self.room3, {'start': '2012-04-01', 'end': '2012-05-12', 'size': 2})
        )
        reservations = group.reservations.all()

        self.assertEqual(len(reservations), 3, 'There should be 3 reservation objects in the returned group')
        self.assertEqual(reservations[0].size, 3, 'First reservation should have size equal to 3')
        self.assertEqual(RoomReservation.objects.count(), initial_reservation_count + 3,
                         'There should be 3 reservation objects added to the database')
        self.assertEqual(TestReservationGroup.objects.count(), initial_group_count + 1,
                         'There should be 1 group object added to the database')

    def test_improper_group_reservation(self):
        initial_reservation_count = RoomReservation.objects.count()
        initial_group_count = TestReservationGroup.objects.count()

        with self.assertRaises(ReservationError):
            TestReservationGroup.reserve(
                (self.room5, {'start': '2012-04-01', 'end': '2012-05-12', 'size': 3}),
                (self.room1, {'start': '2012-04-01', 'end': '2012-05-12', 'size': 1}),
                (self.room3, {'start': '2012-04-01', 'end': '2012-05-12', 'size': 5})
            )

        self.assertEqual(RoomReservation.objects.count(), initial_reservation_count,
                         'There should be no reservation objects added to the database')
        self.assertEqual(TestReservationGroup.objects.count(), initial_group_count,
                         'There should be no group objects added to the database')


class ExclusiveReservationTest(TestCase):
    def setUp(self):
        self.room3 = ConferenceRoom.objects.create(size=3)
        self.room5 = ConferenceRoom.objects.create(size=5)

    def test_cannot_reserve_over_other_reservation(self):
        self.room3.reserve(start='2012-04-01', end='2012-04-02', size=1)
        with self.assertRaises(OverlappingReservations):
            self.room3.reserve(start='2012-04-01', end='2012-04-02', exclusive=True)

        self.room5.reserve(start='2012-04-01', end='2012-04-02', size=1)
        with self.assertRaises(OverlappingReservations):
            self.room5.reserve(start='2012-04-01', end='2012-04-02', exclusive=True)

        self.assertEqual(2, ConferenceRoomReservation.objects.count())

    def test_can_reserve_if_no_overlapping_reservations(self):
        self.assertEqual(5, self.room5.reserve(start='2012-04-01', end='2012-04-02', exclusive=True).size)
        self.assertEqual(5, self.room5.reserve(start='2012-04-02', end='2012-04-04', exclusive=True).size)
        self.assertEqual(5, self.room5.reserve(start='2012-04-05', end='2012-04-07', exclusive=True).size)
        self.assertEqual(3, ConferenceRoomReservation.objects.count())

    def test_exclusive_reservation_always_full(self):
        reservation = self.room5.reserve(start='2012-04-01', end='2012-04-02', exclusive=True)
        self.assertEqual(5, reservation.size)
        self.room5.size = 6
        self.room5.save()
        reservation = self.room5.reservation_model.objects.get(pk=reservation.pk)
        self.assertEqual(6, reservation.size)

    def test_size_must_be_positive(self):
        with self.assertRaises(AssertionError):
            self.room5.reserve(start='2012-04-01', end='2012-04-02', size=0)
        with self.assertRaises(AssertionError):
            self.room5.reserve(start='2012-04-01', end='2012-04-02', size=-1)

    def test_cannot_change_size(self):
        reservation = self.room5.reserve(start='2012-04-01', end='2012-04-02', exclusive=True)
        with self.assertRaises(AttributeError):
            reservation.size = 1

    def test_cannot_set_size(self):
        with self.assertRaises(AttributeError):
            self.room5.reserve(start='2012-04-01', end='2012-04-02', exclusive=True, size=-4)
        with self.assertRaises(AttributeError):
            self.room5.reserve(start='2012-04-01', end='2012-04-02', exclusive=True, size=4)
        with self.assertRaises(AttributeError):
            self.room5.reserve(start='2012-04-01', end='2012-04-02', exclusive=True, size=5)
        with self.assertRaises(AttributeError):
            self.room5.reserve(start='2012-04-01', end='2012-04-02', exclusive=True, size=0)


class ApprovableReservationTest(TestCase):
    def setUp(self):
        self.room1 = RoomWithApprovableReservations.objects.create(size=3)

    def test_valid_pre_reservation_and_valid_reservation(self):
        self.room1.reserve(start='2012-04-01', end='2012-04-02', size=2, valid_until=datetime(2100, 10, 10))
        self.room1.reserve(start='2012-04-01', end='2012-04-02', size=1)

        self.assertEqual(2, ApprovableRoomReservation.objects.with_invalid().count())
        self.assertEqual(2, ApprovableRoomReservation.objects.count())

    def test_valid_pre_reservation_and_invalid_reservation(self):
        self.room1.reserve(start='2012-04-01', end='2012-04-02', size=2, valid_until=datetime(2100, 10, 10))
        with self.assertRaises(SizeExceeded):
            self.room1.reserve(start='2012-04-01', end='2012-04-02', size=2)

        self.assertEqual(1, ApprovableRoomReservation.objects.with_invalid().count())
        self.assertEqual(1, ApprovableRoomReservation.objects.count())

    def test_invalid_pre_reservation_and_valid_reservation(self):
        self.room1.reserve(start='2012-04-01', end='2012-04-02', size=2, valid_until=datetime(2011, 10, 10))
        self.room1.reserve(start='2012-04-01', end='2012-04-02', size=3)

        self.assertEqual(1, ApprovableRoomReservation.objects.count())
        self.assertEqual(2, ApprovableRoomReservation.objects.with_invalid().count())

    def test_valid_reservation(self):
        reservation = self.room1.reserve(
            start=datetime(2012, 4, 1),
            end=datetime(2012, 4, 2),
            size=2,
            valid_until=datetime(2100, 4, 1)
        )
        self.assertTrue(reservation.is_valid())

    def test_invalid_reservation(self):
        reservation = self.room1.reserve(
            start=datetime(2012, 4, 1),
            end=datetime(2012, 4, 2),
            size=2,
            valid_until=datetime(1900, 4, 1)
        )
        self.assertFalse(reservation.is_valid())

        with self.assertRaises(OutdatedReservationError):
            reservation.approve()

    def test_default_validity_period(self):
        with patch('kitabu.models.subjects.now') as dtmock:
            dtmock.return_value = datetime(2012, 1, 1)

            reservation = self.room1.reserve(
                start=datetime(2012, 4, 1),
                end=datetime(2012, 4, 2),
                size=2
            )

        with patch('kitabu.models.reservations.now') as dtmock:
            dtmock.return_value = datetime(2012, 1, 2)
            self.assertTrue(reservation.is_valid())
            self.assertFalse(reservation.approved)

        with patch('kitabu.models.reservations.now') as dtmock:
            dtmock.return_value = datetime(2012, 1, 10)
            self.assertFalse(reservation.is_valid())
            self.assertFalse(reservation.approved)

        with patch('kitabu.models.reservations.now') as dtmock:
            dtmock.return_value = datetime(2012, 1, 10)
            with self.assertRaises(OutdatedReservationError):
                reservation.approve()


def concurrent_reserve(exceptions):
    def real_decorator(func):
        def wrapper():
            try:
                func()
            except Exception, e:
                exceptions.append(e)
                raise
        return wrapper
    return real_decorator


class SimultaneousReservationsTest(TransactionTestCase):
    def setUp(self):
        self.room = Room.objects.create(name="room", size=2)
        self.room2 = Room.objects.create(name="room", size=2)

    def test_simultaneous_reservations(self):
        exceptions = []

        @concurrent_reserve(exceptions)
        def reserve1():
            self.room.reserve(start='2014-04-01', end='2014-04-02', size=2, delay_time=1)

        @concurrent_reserve(exceptions)
        def reserve2():
            sleep(0.5)
            with self.assertRaises(SizeExceeded):
                self.room.reserve(start='2014-04-01', end='2014-04-02', size=2, delay_time=1)

        threads = [Thread(target=reserve1), Thread(target=reserve2)]
        [t.start() for t in threads]
        [t.join() for t in threads]

        if exceptions:
            raise Exception("Intercepted {0} exceptions: {1}".format(len(exceptions), exceptions))

        count = self.room.reservations.count()
        self.assertEqual(count, 1, "Should have only one reservation. Has {0} instead.".format(count))

    def test_simultaneous_group_reservations(self):
        exceptions = []

        @concurrent_reserve(exceptions)
        def reserve1():
            TestReservationGroup.reserve(
                (self.room, {'start': '2014-05-01', 'end': '2014-05-02', 'size': 2}),
                (self.room2, {'start': '2014-05-01', 'end': '2014-05-02', 'size': 2}),
                delay_between_reservations=1,
            )

        @concurrent_reserve(exceptions)
        def reserve2():
            sleep(0.5)
            with self.assertRaises(SizeExceeded):
                TestReservationGroup.reserve(
                    (self.room2, {'start': '2014-05-01', 'end': '2014-05-02', 'size': 2}),
                    (self.room, {'start': '2014-05-01', 'end': '2014-05-02', 'size': 2}),
                    delay_between_reservations=1,
                )

        threads = [Thread(target=reserve1), Thread(target=reserve2)]
        [t.start() for t in threads]
        [t.join() for t in threads]

        if exceptions:
            raise Exception("Intercepted {0} exceptions: {1}".format(len(exceptions), exceptions))

        res_count = RoomReservation.objects.count()
        self.assertEqual(res_count, 2, "There should be only two reservations. {0} instead.".format(res_count))

        group_count = TestReservationGroup.objects.count()
        self.assertEqual(group_count, 1, "There should be only one reservation group. {0} instead.".format(group_count))


class SimultaneousReservationsWithDifferentClassesTest(TransactionTestCase):
    def setUp(self):
        self.room = Room.objects.create(name="room", size=2)
        self.other_room = OtherRoom.objects.create(name="room", size=2)

    def test_simultaneous_group_reservations_with_different_classes(self):
        exceptions = []

        @concurrent_reserve(exceptions)
        def reserve1():
            TestReservationGroup.reserve(
                (self.room, {'start': '2014-05-01', 'end': '2014-05-02', 'size': 2}),
                (self.other_room, {'start': '2014-05-01', 'end': '2014-05-02', 'size': 2}),
                delay_between_reservations=1,
            )

        @concurrent_reserve(exceptions)
        def reserve2():
            sleep(0.5)
            with self.assertRaises(SizeExceeded):
                TestReservationGroup.reserve(
                    (self.other_room, {'start': '2014-05-01', 'end': '2014-05-02', 'size': 2}),
                    (self.room, {'start': '2014-05-01', 'end': '2014-05-02', 'size': 2}),
                    delay_between_reservations=1,
                )

        threads = [Thread(target=reserve1), Thread(target=reserve2)]
        [t.start() for t in threads]
        [t.join() for t in threads]

        if exceptions:
            raise Exception("Intercepted {0} exceptions: {1}".format(len(exceptions), exceptions))

        res_count = RoomReservation.objects.count()
        self.assertEqual(
            res_count, 1, "There should be only one reservation for Room class. {0} instead.".format(res_count))

        other_res_count = OtherRoomReservation.objects.count()
        self.assertEqual(
            other_res_count, 1,
            "There should be only one reservation for OtherRoom class. {0} instead.".format(other_res_count))

        group_count = TestReservationGroup.objects.count()
        self.assertEqual(group_count, 1, "There should be only one reservation group. {0} instead.".format(group_count))
