import datetime

from django.test import SimpleTestCase
from django.contrib.auth.models import User

from kitabu.tests.models import Room, RoomReservation, Hotel, HotelRoom, HotelRoomReservation
from kitabu.tests.utils import parse_date
from kitabu.forms.availability import (
    #VaryingDateAvailabilityForm,
    VaryingDateAndSizeAvailabilityForm,
    ClusterFiniteAvailabilityForm
)

# Base VaryingDateAvailabilityForm class in not tested as the only difference
# from VaryingDateAndSizeAvailabilityForm is fixed size of 1


class VaryingDateAndSizeAvailabilityFormTest(SimpleTestCase):
    def setUp(self):
        '''
        For clean reading room1 has size of 1, room2 size of 2, and room3 - size 3.
        '''
        Room.objects.all().delete()
        RoomReservation.objects.all().delete()
        User.objects.all().delete()

        self.room1 = Room.objects.create(name='Room 1', size=1)
        self.room2 = Room.objects.create(name='Room 2', size=2)
        self.room3 = Room.objects.create(name='Room 3', size=3)

        self.user = User.objects.create_user('user', 'user@example.com')

    def test_whole_period_available(self):
        RoomReservation.objects.create(
            subject=self.room1,
            size=1,
            owner=self.user,
            start=datetime.datetime(2001, 1, 1),
            end=datetime.datetime(2001, 1, 8)
        )
        start = '2000-01-01'
        end = '2000-01-31'
        data = {
            'start': start,
            'end': end,
            'duration': 7,
            'size': 1,
        }
        form = VaryingDateAndSizeAvailabilityForm(data)
        self.assertTrue(form.is_valid())
        self.assertEqual(
            form.search(subject=self.room1),
            [(parse_date(start), parse_date(end))]
        )

    def test_begin_of_period_unavailable(self):
        reservation = RoomReservation.objects.create(
            subject=self.room1,
            size=1,
            owner=self.user,
            start=datetime.datetime(2001, 1, 1),
            end=datetime.datetime(2001, 1, 8)
        )
        start = '2001-01-01'
        end = '2001-01-31'
        data = {
            'start': start,
            'end': end,
            'duration': 7,
            'size': 1,
        }
        form = VaryingDateAndSizeAvailabilityForm(data)
        self.assertTrue(form.is_valid())
        self.assertEqual(
            form.search(subject=self.room1),
            [(reservation.end, parse_date(end))]
        )

    def test_middle_of_period_unavailable(self):
        reservation = RoomReservation.objects.create(
            subject=self.room1,
            size=1,
            owner=self.user,
            start=datetime.datetime(2001, 1, 1),
            end=datetime.datetime(2001, 1, 8)
        )
        start = '2000-12-01'
        end = '2001-01-31'
        data = {
            'start': start,
            'end': end,
            'duration': 7,
            'size': 1,
        }
        form = VaryingDateAndSizeAvailabilityForm(data)
        self.assertTrue(form.is_valid())
        self.assertEqual(
            form.search(subject=self.room1),
            [
                (parse_date(start), reservation.start),
                (reservation.end, parse_date(end))
            ]
        )

    def test_whole_period_available_but_with_concurrent_reservation(self):
        RoomReservation.objects.create(
            subject=self.room2,
            size=1,
            owner=self.user,
            start=datetime.datetime(2001, 1, 1),
            end=datetime.datetime(2001, 1, 8)
        )
        start = '2001-01-01'
        end = '2001-01-31'
        data = {
            'start': start,
            'end': end,
            'duration': 7,
            'size': 1,
        }
        form = VaryingDateAndSizeAvailabilityForm(data)
        self.assertTrue(form.is_valid())
        self.assertEqual(
            form.search(subject=self.room2),
            [
                (parse_date(start), parse_date(end))
            ]
        )

    def test_middle_of_period_unavailable_one_place_missing(self):
        reservation = RoomReservation.objects.create(
            subject=self.room3,
            size=1,
            owner=self.user,
            start=datetime.datetime(2001, 1, 8),
            end=datetime.datetime(2001, 1, 15)
        )  # this reservation will not collide as it has size one, leaving 2 places available

        reservation = RoomReservation.objects.create(
            subject=self.room3,
            size=2,
            owner=self.user,
            start=datetime.datetime(2001, 1, 1),
            end=datetime.datetime(2001, 1, 8)
        )
        start = '2000-12-01'
        end = '2001-01-31'
        data = {
            'start': start,
            'end': end,
            'duration': 7,
            'size': 2,
        }
        form = VaryingDateAndSizeAvailabilityForm(data)
        self.assertTrue(form.is_valid())
        self.assertEqual(
            form.search(subject=self.room3),
            [
                (parse_date(start), reservation.start),
                (reservation.end, parse_date(end))
            ]
        )

    def test_period_unavailable(self):
        day = lambda day: datetime.datetime(2001, 1, day)
        reserve = lambda start, end, size: RoomReservation.objects.create(
            subject=self.room3,
            size=size,
            owner=self.user,
            start=start,
            end=end
        )

        reserve(day(1), day(4), 3)
        reserve(day(4), day(7), 1)
        reserve(day(6), day(11), 1)
        reserve(day(8), day(15), 2)
        reserve(day(22), day(29), 2)

        start = '2001-01-01'
        end = '2001-01-31'
        data = {
            'start': start,
            'end': end,
            'duration': 8,
            'size': 2,
        }
        form = VaryingDateAndSizeAvailabilityForm(data)
        self.assertTrue(form.is_valid())
        self.assertEqual(
            form.search(subject=self.room3),
            []
        )


class ClusterFiniteAvailabilityFormTest(SimpleTestCase):
    def setUp(self):
        '''
        All rooms in hotel1 have size of 5. Size of 10 in hotel2.
        '''
        Hotel.objects.all().delete()
        HotelRoom.objects.all().delete()
        HotelRoomReservation.objects.all().delete()
        User.objects.all().delete()

        self.hotel1 = Hotel.objects.create(name='Hotel 1')
        self.hotel2 = Hotel.objects.create(name='Hotel 2')

        self.room1 = HotelRoom.objects.create(name='Room 1', size=5, cluster=self.hotel1)
        self.room2 = HotelRoom.objects.create(name='Room 2', size=5, cluster=self.hotel1)
        self.room3 = HotelRoom.objects.create(name='Room 3', size=10, cluster=self.hotel2)
        self.room4 = HotelRoom.objects.create(name='Room 3', size=10, cluster=self.hotel2)

    def test_empty_clusters(self):
        start = '2001-01-01'
        end = '2001-01-31'
        data = {
            'start': start,
            'end': end,
            'size': 11,
        }
        formClass = ClusterFiniteAvailabilityForm.on_models(HotelRoom, Hotel, 'rooms')
        form = formClass(data)
        self.assertTrue(form.is_valid(), 'Form should be valid')

        results = form.search()
        self.assertEqual(len(results), 1, 'There should be one hotel returned')
        self.assertEqual(results[0].name, 'Hotel 2', 'Hotel 2 should be returned')

    def test_all_reservations_overlapping(self):
        self.room1.reserve(start='2000-12-30', end='2001-01-22', size=1)
        self.room1.reserve(start='2000-11-30', end='2001-01-21', size=1)
        self.room2.reserve(start='2001-01-20', end='2001-02-11', size=2)

        self.room3.reserve(start='2001-01-05', end='2001-01-14', size=4)
        self.room3.reserve(start='2001-01-10', end='2001-01-17', size=4)
        self.room4.reserve(start='2000-12-20', end='2001-02-18', size=7)

        start = '2001-01-01'
        end = '2001-01-31'
        data = {
            'start': start,
            'end': end,
            'size': 6,
        }
        formClass = ClusterFiniteAvailabilityForm.on_models(HotelRoom, Hotel, 'rooms')
        form = formClass(data)
        self.assertTrue(form.is_valid(), 'Form should be valid')

        results = form.search()
        self.assertEqual(len(results), 1, 'There should be one hotel returned')
        self.assertEqual(results[0].name, 'Hotel 1', 'Hotel 1 should be returned')

    def test_the_need_to_switch_room(self):
        self.room3.reserve(start='2001-01-01', end='2001-01-15', size=5)
        self.room4.reserve(start='2001-01-01', end='2001-01-15', size=7)

        self.room3.reserve(start='2001-01-16', end='2001-01-25', size=7)
        self.room4.reserve(start='2001-01-16', end='2001-01-25', size=5)

        start = '2001-01-01'
        end = '2001-01-31'
        data = {
            'start': start,
            'end': end,
            'size': 7,
        }
        formClass = ClusterFiniteAvailabilityForm.on_models(HotelRoom, Hotel, 'rooms')
        form = formClass(data)
        self.assertTrue(form.is_valid(), 'Form should be valid')

        results = form.search()
        length = len(results)
        self.assertEqual(length, 1, 'There should be one hotel returned. ' + str(length) + ' hotels returned instead')
        self.assertEqual(results[0].name, 'Hotel 1', 'Hotel 1 should be returned')
