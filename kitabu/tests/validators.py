from datetime import datetime

from mock import Mock

from django.test import TestCase

from kitabu.exceptions import ValidationError

from kitabu.tests.models import FullTimeValidator


class FullTimeValidatorTest(TestCase):

    def test_half_a_minute(self):
        reservation = Mock()
        validator = FullTimeValidator.objects.create(interval_type='second', interval=30)

        reservation.start = datetime(2000, 01, 01, 16, 40)
        validator.validate(reservation)

        reservation.start = datetime(2000, 01, 01, 16, 40, 0, 0)
        validator.validate(reservation)

        reservation.start = datetime(2000, 01, 01, 16, 40, 30, 0)
        validator.validate(reservation)

        with self.assertRaises(ValidationError):
            reservation.start = datetime(2000, 01, 01, 16, 40, 15)
            validator.validate(reservation)

        with self.assertRaises(ValidationError):
            reservation.start = datetime(2000, 01, 01, 16, 40, 0, 1)
            validator.validate(reservation)

    def test_full_hour_zero_minures(self):
        reservation = Mock()
        validator = FullTimeValidator.objects.create(interval_type='minute', interval=0)

        reservation.start = datetime(2000, 01, 01, 16, 0)
        validator.validate(reservation)

        with self.assertRaises(ValidationError):
            reservation.start = datetime(2000, 01, 01, 16, 40, 0, 1)
            validator.validate(reservation)

        with self.assertRaises(ValidationError):
            reservation.start = datetime(2000, 01, 01, 16, 0, 0, 1)
            validator.validate(reservation)

    def test_full_hour_60_minutes(self):
        reservation = Mock()
        validator = FullTimeValidator.objects.create(interval_type='minute', interval=60)

        reservation.start = datetime(2000, 01, 01, 16, 0)
        validator.validate(reservation)

        with self.assertRaises(ValidationError):
            reservation.start = datetime(2000, 01, 01, 16, 40, 0, 0)
            validator.validate(reservation)

        with self.assertRaises(ValidationError):
            reservation.start = datetime(2000, 01, 01, 16, 0, 0, 1)
            validator.validate(reservation)

    def test_many_fields(self):
        FullTimeValidator._get_date_field_names = Mock(return_value=['start', 'end'])
        reservation = Mock()
        validator = FullTimeValidator.objects.create(interval_type='hour', interval=2)

        reservation.start = reservation.end = datetime(2000, 01, 01, 16, 0)
        validator.validate(reservation)

        reservation.start = datetime(2000, 01, 01, 14, 0)
        reservation.end = datetime(2000, 01, 01, 16, 0)
        validator.validate(reservation)

        with self.assertRaises(ValidationError):
            reservation.start = datetime(2000, 01, 01, 15, 00, 0, 0)
            reservation.end = datetime(2000, 01, 01, 16, 0)
            validator.validate(reservation)

        with self.assertRaises(ValidationError):
            reservation.start = datetime(2000, 01, 01, 16, 0, 0, 0)
            reservation.end = datetime(2000, 01, 01, 17, 0, 0, 0)
            validator.validate(reservation)

        with self.assertRaises(ValidationError):
            reservation.start = datetime(2000, 01, 01, 15, 0, 0, 0)
            reservation.end = datetime(2000, 01, 01, 17, 0, 0, 0)
            validator.validate(reservation)
