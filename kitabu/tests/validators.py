from datetime import datetime

from mock import Mock

from django.test import TestCase

from kitabu.exceptions import ValidationError

from kitabu.tests.models import FullTimeValidator, StaticValidator


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


class StaticValidatorTest(TestCase):

    def test_failing_validator(self):
        reservation = Mock()
        validator = StaticValidator.objects.create(
            validator_function_absolute_name='kitabu.tests.validators.StaticValidatorTest.fail')

        with self.assertRaises(ValidationError):
            validator.validate(reservation)

    def test_passing_validator(self):
        reservation = Mock()
        validator = StaticValidator.objects.create(
            validator_function_absolute_name='kitabu.tests.validators.StaticValidatorTest.pass_')

        validator.validate(reservation)

    def test_fail_for_a_reason_validator(self):
        reservation = Mock()
        validator = StaticValidator.objects.create(
            validator_function_absolute_name='kitabu.tests.validators.StaticValidatorTest.fail_for_a_reason')

        validator.validate(None)
        reservation.reason = Mock(return_value=False)
        validator.validate(reservation)
        reservation.reason.assert_called_once_with()
        reservation.reason = Mock(return_value=True)
        with self.assertRaises(ValidationError):
            validator.validate(reservation)
        reservation.reason.assert_called_once_with()

    def test_incorrect_validator_function_path(self):
        with self.assertRaises(AttributeError):
            StaticValidator.objects.create(validator_function_absolute_name=
                                           'kitabu.tests.validators.StaticValidatorTest.non_existant_func')

    def test_incorrect_validator_function_path_forced(self):
        validator = StaticValidator(validator_function_absolute_name=
                                    'kitabu.tests.validators.StaticValidatorTest.non_existant_func')
        validator.save(force_validation_function_name=True)

    @staticmethod
    def fail(reservation):
        raise ValidationError()

    @staticmethod
    def pass_(reservation):
        pass

    @staticmethod
    def fail_for_a_reason(reservation):
        if hasattr(reservation, 'reason'):
            if reservation.reason():
                raise ValidationError()
