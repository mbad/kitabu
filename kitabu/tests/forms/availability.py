import datetime

from django.test import SimpleTestCase
from django.contrib.auth.models import User

from kitabu.tests.models import Room, RoomReservation
from kitabu.tests.utils import parse_date
from kitabu.forms.availability import (
    #VaryingDateAvailabilityForm,
    VaryingDateAndSizeAvailabilityForm,
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
