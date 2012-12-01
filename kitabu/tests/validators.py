from datetime import datetime

from mock import Mock, patch

from django.test import TestCase

from kitabu.exceptions import ValidationError

from kitabu.tests.models import (
    FullTimeValidator,
    StaticValidator,
    LateEnoughValidator,
    NotSoonerThanValidator,
    NotLaterThanValidator,
    WithinPeriodValidator,
    NotWithinPeriodValidator,
    GivenHoursAndWeekdaysValidator,
    Room,
)

# TODO:
# NotSoonerThanValidator._get_date_field_names = Mock(return_value=['begin'])
# patching this way is evil as it is permanent and may affect proceeding tests.
# Maybe this can be done better.


class SubjectWithValidatorTest(TestCase):
    def setUp(self):
        self.room = Room.objects.create(name="room", size=200)
        self.three_minutes_validator = FullTimeValidator.objects.create(interval_type='minute', interval=3)
        self.room.validators.add(self.three_minutes_validator)

    def test_proper_reservation(self):
        initial_count = self.room.reservations.count()

        start = datetime(2000, 01, 01, 16, 06)
        end = datetime(2000, 01, 01, 16, 21)
        self.room.reserve(start=start, end=end, size=1)

        current_count = self.room.reservations.count()
        self.assertEqual(current_count, initial_count + 1,
                         'There should be one reservation object added to the database')

    def test_improper_reservation(self):
        initial_count = self.room.reservations.count()

        start = datetime(2000, 01, 01, 16, 07)
        end = datetime(2000, 01, 01, 16, 21)
        with self.assertRaises(ValidationError):
            self.room.reserve(start=start, end=end, size=1)

        current_count = self.room.reservations.count()
        self.assertEqual(current_count, initial_count, 'There should be no reservation objects added to the database')


class SubjectAndUniversalValidatorTest(TestCase):
    def setUp(self):
        self.room = Room.objects.create(name="room", size=200)
        FullTimeValidator.objects.create(interval_type='minute', interval=3, apply_to_all=True)

    def test_proper_reservation(self):
        initial_count = self.room.reservations.count()

        start = datetime(2000, 01, 01, 16, 06)
        end = datetime(2000, 01, 01, 16, 21)
        self.room.reserve(start=start, end=end, size=1)

        current_count = self.room.reservations.count()
        self.assertEqual(current_count, initial_count + 1,
                         'There should be one reservation object added to the database')

    def test_improper_reservation(self):
        initial_count = self.room.reservations.count()

        start = datetime(2000, 01, 01, 16, 07)
        end = datetime(2000, 01, 01, 16, 21)
        with self.assertRaises(ValidationError):
            self.room.reserve(start=start, end=end, size=1)

        current_count = self.room.reservations.count()
        self.assertEqual(current_count, initial_count, 'There should be no reservation objects added to the database')


class FullTimeValidatorTest(TestCase):

    def test_half_a_minute(self):
        reservation = Mock()
        validator = FullTimeValidator.objects.create(interval_type='second', interval=30)
        FullTimeValidator._get_date_field_names = Mock(return_value=['start'])

        reservation.start = datetime(2000, 1, 1, 16, 40)
        validator.validate(reservation)

        reservation.start = datetime(2000, 1, 1, 16, 40, 0, 0)
        validator.validate(reservation)

        reservation.start = datetime(2000, 1, 1, 16, 40, 30, 0)
        validator.validate(reservation)

        with self.assertRaises(ValidationError):
            reservation.start = datetime(2000, 1, 1, 16, 40, 15)
            validator.validate(reservation)

        with self.assertRaises(ValidationError):
            reservation.start = datetime(2000, 1, 1, 16, 40, 0, 1)
            validator.validate(reservation)

    def test_full_hour_zero_minures(self):
        reservation = Mock()
        validator = FullTimeValidator.objects.create(interval_type='minute', interval=0)
        FullTimeValidator._get_date_field_names = Mock(return_value=['start'])

        reservation.start = datetime(2000, 1, 1, 16, 0)
        validator.validate(reservation)

        with self.assertRaises(ValidationError):
            reservation.start = datetime(2000, 1, 1, 16, 40, 0, 1)
            validator.validate(reservation)

        with self.assertRaises(ValidationError):
            reservation.start = datetime(2000, 1, 1, 16, 0, 0, 1)
            validator.validate(reservation)

    def test_full_hour_60_minutes(self):
        reservation = Mock()
        validator = FullTimeValidator.objects.create(interval_type='minute', interval=60)
        FullTimeValidator._get_date_field_names = Mock(return_value=['start'])

        reservation.start = datetime(2000, 1, 1, 16, 0)
        validator.validate(reservation)

        with self.assertRaises(ValidationError):
            reservation.start = datetime(2000, 1, 1, 16, 40, 0, 0)
            validator.validate(reservation)

        with self.assertRaises(ValidationError):
            reservation.start = datetime(2000, 1, 1, 16, 0, 0, 1)
            validator.validate(reservation)

    def test_many_fields(self):
        FullTimeValidator._get_date_field_names = Mock(return_value=['start', 'end'])
        reservation = Mock()
        validator = FullTimeValidator.objects.create(interval_type='hour', interval=2)

        reservation.start = reservation.end = datetime(2000, 1, 1, 16, 0)
        validator.validate(reservation)

        reservation.start = datetime(2000, 1, 1, 14, 0)
        reservation.end = datetime(2000, 1, 1, 16, 0)
        validator.validate(reservation)

        with self.assertRaises(ValidationError):
            reservation.start = datetime(2000, 1, 1, 15, 0, 0, 0)
            reservation.end = datetime(2000, 1, 1, 16, 0)
            validator.validate(reservation)

        with self.assertRaises(ValidationError):
            reservation.start = datetime(2000, 1, 1, 16, 0, 0, 0)
            reservation.end = datetime(2000, 1, 1, 17, 0, 0, 0)
            validator.validate(reservation)

        with self.assertRaises(ValidationError):
            reservation.start = datetime(2000, 1, 1, 15, 0, 0, 0)
            reservation.end = datetime(2000, 1, 1, 17, 0, 0, 0)
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
            StaticValidator.objects.create(
                validator_function_absolute_name='kitabu.tests.validators.StaticValidatorTest.non_existant_func')

    def test_incorrect_validator_function_path_forced(self):
        validator = StaticValidator(
            validator_function_absolute_name='kitabu.tests.validators.StaticValidatorTest.non_existant_func')
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


class FarEnoughValidatorTest(TestCase):

    def setup_and_patch_5_days(method):
        '''
        This method is a hack and is meant to be called only as decorator of other methods in this class.

        This uses python language definition as follows:
            when class is constructed, class body is executed - by the time methods in this class are not bound,
            so this method will be just a function - and we use this function to decorate other methods.
        '''
        def new_method(self):
            self.reservation = Mock()
            self.validator = LateEnoughValidator.objects.create(time_unit='day', time_value=5)
            LateEnoughValidator._get_date_field_names = Mock(return_value=['start', 'end'])

            with patch('kitabu.models.validators.now') as dtmock:
                dtmock.return_value = datetime(2000, 1, 1)

                method(self)
        return new_method

    @setup_and_patch_5_days
    def test_today_is_too_soon(self):
        self.reservation.start = datetime(2000, 1, 1)
        self.reservation.end = datetime(2000, 1, 1)

        with self.assertRaises(ValidationError):
            self.validator.validate(self.reservation)

    @setup_and_patch_5_days
    def test_too_soon(self):
        self.reservation.start = datetime(2000, 1, 3)
        self.reservation.end = datetime(2000, 1, 3)

        with self.assertRaises(ValidationError):
            self.validator.validate(self.reservation)

    @setup_and_patch_5_days
    def test_past_is_too_soon(self):
        self.reservation.start = datetime(1999, 4, 1)
        self.reservation.end = datetime(1999, 5, 1)

        with self.assertRaises(ValidationError):
            self.validator.validate(self.reservation)

    @setup_and_patch_5_days
    def test_slightly_too_soon(self):
        self.reservation.start = datetime(2000, 1, 5, 23, 59)
        self.reservation.end = datetime(2000, 1, 5, 23, 59)

        with self.assertRaises(ValidationError):
            self.validator.validate(self.reservation)

    @setup_and_patch_5_days
    def test_as_soon_as_it_gets(self):
        self.reservation.start = datetime(2000, 1, 6, 0, 0)
        self.reservation.end = datetime(2000, 1, 6, 0, 0)

        self.validator.validate(self.reservation)

    @setup_and_patch_5_days
    def test_much_later(self):
        self.reservation.start = datetime(2000, 1, 16, 0, 0)
        self.reservation.end = datetime(2000, 1, 26, 0, 0)

        self.validator.validate(self.reservation)

    def test_an_hour_too_soon_start(self):
        self.reservation = Mock()
        self.validator = LateEnoughValidator.objects.create(time_unit='minute', time_value=15)
        self.validator._get_date_field_names = Mock(return_value=['start'])

        with patch('kitabu.models.validators.now') as dtmock:
            dtmock.return_value = datetime(2000, 1, 1)

            self.reservation.start = datetime(1999, 12, 31, 23, 15)
            self.reservation.end = datetime(2000, 1, 26, 0, 0)

            with self.assertRaises(ValidationError):
                self.validator.validate(self.reservation)

    def test_a_quarter_too_soon_start(self):
        self.reservation = Mock()
        self.validator = LateEnoughValidator.objects.create(time_unit='minute', time_value=45)
        LateEnoughValidator._get_date_field_names = Mock(return_value=['start'])

        with patch('kitabu.models.validators.now') as dtmock:
            dtmock.return_value = datetime(2000, 1, 1)

            self.reservation.start = datetime(2000, 1, 1, 0, 30)

            with self.assertRaises(ValidationError):
                self.validator.validate(self.reservation)

    def test_just_in_time(self):
        self.reservation = Mock()
        self.validator = LateEnoughValidator.objects.create(time_unit='minute', time_value=30)
        LateEnoughValidator._get_date_field_names = Mock(return_value=['start'])

        with patch('kitabu.models.validators.now') as dtmock:
            dtmock.return_value = datetime(2000, 1, 1)

            self.reservation.start = datetime(2000, 1, 1, 0, 30)

            self.validator.validate(self.reservation)


class NotSoonerThanValidatorTest(TestCase):

    def test_with_begin_field(self):
        validator = NotSoonerThanValidator.objects.create(date=datetime(2000, 1, 2))
        NotSoonerThanValidator._get_date_field_names = Mock(return_value=['begin'])
        reservation = Mock()

        reservation.begin = datetime(2000, 1, 2)
        validator.validate(reservation)

        with self.assertRaises(ValidationError):
            reservation.begin = datetime(2000, 1, 1)
            validator.validate(reservation)

    def test_with_start_end_fields(self):
        validator = NotSoonerThanValidator.objects.create(date=datetime(2000, 1, 2))
        NotSoonerThanValidator._get_date_field_names = Mock(return_value=['start', 'end'])
        reservation = Mock()

        reservation.start = datetime(2000, 1, 1)
        reservation.end = datetime(2000, 1, 1)

        with self.assertRaises(ValidationError):
            validator.validate(reservation)

        reservation.start = datetime(2000, 1, 3)
        reservation.end = datetime(2000, 1, 1)

        with self.assertRaises(ValidationError):
            validator.validate(reservation)

        reservation.start = datetime(2000, 1, 1)
        reservation.end = datetime(2000, 1, 4)

        with self.assertRaises(ValidationError):
            validator.validate(reservation)

        reservation.start = datetime(2000, 1, 1, 16)
        reservation.end = datetime(2000, 1, 4)


class NotLaterThanValidatorTest(TestCase):

    def test_with_begin_field(self):
        validator = NotLaterThanValidator.objects.create(date=datetime(2000, 1, 2))
        NotLaterThanValidator._get_date_field_names = Mock(return_value=['begin'])
        reservation = Mock()

        reservation.begin = datetime(2000, 1, 2)
        validator.validate(reservation)

        with self.assertRaises(ValidationError):
            reservation.begin = datetime(2000, 1, 3)
            validator.validate(reservation)

    def test_with_start_end_fields(self):
        validator = NotLaterThanValidator.objects.create(date=datetime(2000, 1, 2))
        NotLaterThanValidator._get_date_field_names = Mock(return_value=['start', 'end'])
        reservation = Mock()

        reservation.start = datetime(2000, 1, 1)
        reservation.end = datetime(2000, 1, 3)

        with self.assertRaises(ValidationError):
            validator.validate(reservation)

        reservation.start = datetime(2000, 1, 3)
        reservation.end = datetime(2000, 1, 1)

        with self.assertRaises(ValidationError):
            validator.validate(reservation)

        reservation.start = datetime(2000, 1, 3)
        reservation.end = datetime(2000, 1, 4)

        with self.assertRaises(ValidationError):
            validator.validate(reservation)

        reservation.start = datetime(2000, 1, 1, 16)
        reservation.end = datetime(2000, 1, 1)
        validator.validate(reservation)


class WithinPeriodTest(TestCase):

    def test_with_begin_field(self):
        validator = WithinPeriodValidator.objects.create(start=datetime(2000, 1, 2),
                                                         end=datetime(2000, 1, 4))
        WithinPeriodValidator._get_date_field_names = Mock(return_value=['begin'])
        reservation = Mock()

        reservation.begin = datetime(2000, 1, 2)
        validator.validate(reservation)

        reservation.begin = datetime(2000, 1, 3)
        validator.validate(reservation)

        reservation.begin = datetime(2000, 1, 4)
        validator.validate(reservation)

        with self.assertRaises(ValidationError):
            reservation.begin = datetime(2000, 1, 1)
            validator.validate(reservation)

        with self.assertRaises(ValidationError):
            reservation.begin = datetime(2000, 1, 5)
            validator.validate(reservation)

        with self.assertRaises(ValidationError):
            reservation.begin = datetime(2002, 1, 5)
            validator.validate(reservation)

        with self.assertRaises(ValidationError):
            reservation.begin = datetime(1998, 1, 3)
            validator.validate(reservation)

    def test_with_start_end_fields(self):
        validator = WithinPeriodValidator.objects.create(start=datetime(2000, 1, 2),
                                                         end=datetime(2000, 1, 4))
        WithinPeriodValidator._get_date_field_names = Mock(return_value=['start', 'end'])
        reservation = Mock()

        reservation.start = datetime(2000, 1, 2)
        reservation.end = datetime(2000, 1, 4)

        validator.validate(reservation)

        reservation.start = datetime(2000, 1, 3)
        reservation.end = datetime(2000, 1, 1)

        with self.assertRaises(ValidationError):
            validator.validate(reservation)

        reservation.start = datetime(2000, 1, 4)
        reservation.end = datetime(2000, 1, 3)

        validator.validate(reservation)

        reservation.start = datetime(2000, 1, 1, 16)
        reservation.end = datetime(2000, 1, 2)

        with self.assertRaises(ValidationError):
            validator.validate(reservation)

        reservation.start = datetime(2000, 1, 3)
        reservation.end = datetime(2000, 1, 1)

        with self.assertRaises(ValidationError):
            validator.validate(reservation)

        reservation.start = datetime(2000, 1, 6)
        reservation.end = datetime(2000, 1, 4)

        with self.assertRaises(ValidationError):
            validator.validate(reservation)

        reservation.start = datetime(2000, 1, 1)
        reservation.end = datetime(2000, 1, 14)

        with self.assertRaises(ValidationError):
            validator.validate(reservation)

        reservation.start = datetime(2001, 1, 1)
        reservation.end = datetime(2001, 1, 14)

        with self.assertRaises(ValidationError):
            validator.validate(reservation)


class NotWithinPeriodTest(TestCase):

    def test_with_start_end_fields(self):
        validator = NotWithinPeriodValidator.objects.create(start=datetime(2000, 1, 2),
                                                            end=datetime(2000, 1, 4))
        NotWithinPeriodValidator._get_date_field_names = Mock(return_value=['start', 'end'])
        reservation = Mock()

        reservation.start = datetime(2000, 1, 2)
        reservation.end = datetime(2000, 1, 4)

        with self.assertRaises(ValidationError):
            validator.validate(reservation)

        reservation.start = datetime(2000, 1, 3)
        reservation.end = datetime(2000, 1, 1)

        with self.assertRaises(ValidationError):
            validator.validate(reservation)

        reservation.start = datetime(2000, 1, 4)
        reservation.end = datetime(2000, 1, 3)

        with self.assertRaises(ValidationError):
            validator.validate(reservation)

        reservation.start = datetime(2000, 1, 1, 16)
        reservation.end = datetime(2000, 1, 2)

        with self.assertRaises(ValidationError):
            validator.validate(reservation)

        reservation.start = datetime(2000, 1, 3)
        reservation.end = datetime(2000, 1, 1)

        with self.assertRaises(ValidationError):
            validator.validate(reservation)

        reservation.start = datetime(2000, 1, 6)
        reservation.end = datetime(2000, 1, 4)

        with self.assertRaises(ValidationError):
            validator.validate(reservation)

        reservation.start = datetime(2000, 1, 1)
        reservation.end = datetime(2000, 1, 14)

        with self.assertRaises(ValidationError):
            validator.validate(reservation)

        reservation.start = datetime(2001, 1, 1)
        reservation.end = datetime(2001, 1, 14)

        validator.validate(reservation)


class GivenHoursAndDaysTest(TestCase):

    def setUp(self):
        # 0 - 2 ok, 3 - 6 wrong, 7 - 11 ok, 12 - 14 wrong, 15 - 19 ok, 20 - 21 wrong, 22 - 23 ok
        self.hours = [1, 1, 1, 0, 0, 0, 0, 1, 1, 1, 1, 1, 0, 0, 0, 1, 1, 1, 1, 1, 0, 0, 1, 1]
        # Monday, Tuesday, Thursday, Friday and Sunday ok, Wednesday and Saturday wrong
        self.days = [1, 1, 0, 1, 1, 0, 1]
        self.hours_validator = GivenHoursAndWeekdaysValidator.create_from_bitlists(days=[1] * 7, hours=self.hours)
        self.days_validator = GivenHoursAndWeekdaysValidator.create_from_bitlists(days=self.days, hours=[1] * 24)
        self.all_validator = GivenHoursAndWeekdaysValidator.create_from_bitlists(hours=[1] * 24, days=[1] * 7)
        self.reservation = Mock

    def test_valid_hours_same_day(self):
        self.reservation.start = datetime(2012, 11, 27, 15, 15)
        self.reservation.end = datetime(2012, 11, 27, 18, 45)
        self.hours_validator.validate(self.reservation)

    def test_valid_hours_one_day_difference(self):
        self.reservation.start = datetime(2012, 11, 26, 22, 15)
        self.reservation.end = datetime(2012, 11, 27, 1, 45)
        self.hours_validator.validate(self.reservation)

    def test_valid_hours_one_day_difference_all_hours(self):
        self.reservation.start = datetime(2012, 11, 27, 15, 15)
        self.reservation.end = datetime(2012, 11, 28, 14, 45)
        self.all_validator.validate(self.reservation)

    def test_valid_hours_two_days_difference(self):
        self.reservation.start = datetime(2012, 11, 27, 15, 15)
        self.reservation.end = datetime(2012, 11, 29, 14, 45)
        self.all_validator.validate(self.reservation)

    def test_valid_days_same_week(self):
        # Monday - Tuesday
        self.reservation.start = datetime(2012, 11, 26)
        self.reservation.end = datetime(2012, 11, 27)
        self.days_validator.validate(self.reservation)

    def test_valid_days_one_week_difference(self):
        # Sunday - Tuesday
        self.reservation.start = datetime(2012, 11, 18)
        self.reservation.end = datetime(2012, 11, 20)
        self.days_validator.validate(self.reservation)

    def test_valid_days_one_week_difference_all_days(self):
        self.reservation.start = datetime(2012, 11, 21)
        self.reservation.end = datetime(2012, 11, 27)
        self.all_validator.validate(self.reservation)

    def test_valid_days_two_weeks_difference(self):
        self.reservation.start = datetime(2012, 11, 20)
        self.reservation.end = datetime(2012, 12, 2)
        self.all_validator.validate(self.reservation)

    # Invalid data

    def test_invalid_hours_same_day(self):
        self.reservation.start = datetime(2012, 11, 27, 15, 15)
        self.reservation.end = datetime(2012, 11, 27, 22, 45)
        with self.assertRaises(ValidationError):
            self.hours_validator.validate(self.reservation)

    def test_invalid_hours_one_day_difference(self):
        self.reservation.start = datetime(2012, 11, 26, 22, 15)
        self.reservation.end = datetime(2012, 11, 27, 3, 45)
        with self.assertRaises(ValidationError):
            self.hours_validator.validate(self.reservation)

    def test_invalid_hours_one_day_difference_all_hours(self):
        self.reservation.start = datetime(2012, 11, 27, 15, 15)
        self.reservation.end = datetime(2012, 11, 28, 14, 45)
        with self.assertRaises(ValidationError):
            self.hours_validator.validate(self.reservation)

    def test_invalid_hours_two_days_difference(self):
        self.reservation.start = datetime(2012, 11, 27, 15, 15)
        self.reservation.end = datetime(2012, 11, 29, 14, 45)
        with self.assertRaises(ValidationError):
            self.hours_validator.validate(self.reservation)

    def test_invalid_days_same_week(self):
        # Monday - Friday
        self.reservation.start = datetime(2012, 11, 26)
        self.reservation.end = datetime(2012, 11, 30)
        with self.assertRaises(ValidationError):
            self.days_validator.validate(self.reservation)

    def test_invalid_days_one_week_difference(self):
        # Friday - Tuesday
        self.reservation.start = datetime(2012, 11, 23)
        self.reservation.end = datetime(2012, 11, 27)
        with self.assertRaises(ValidationError):
            self.days_validator.validate(self.reservation)

    def test_invalid_days_one_week_difference_all_days(self):
        self.reservation.start = datetime(2012, 11, 21)
        self.reservation.end = datetime(2012, 11, 27)
        with self.assertRaises(ValidationError):
            self.days_validator.validate(self.reservation)

    def test_invalid_days_two_weeks_difference(self):
        self.reservation.start = datetime(2012, 11, 20)
        self.reservation.end = datetime(2012, 12, 2)
        with self.assertRaises(ValidationError):
            self.days_validator.validate(self.reservation)


class MaxDurationValidatorTest(TestCase):
    def test_max_len(self):
        pass
        # TODO
