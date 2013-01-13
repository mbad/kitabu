from datetime import datetime

from mock import Mock, patch

from django.test import TestCase

from kitabu.exceptions import ValidationError

from kitabu.tests.models import (
    FullTimeValidator,
    StaticValidator,
    TimeIntervalValidator,
    WithinPeriodValidator,
    NotWithinPeriodValidator,
    GivenHoursAndWeekdaysValidator,
    MaxDurationValidator,
    Room,
    Period,
)

# TODO:
# Class._get_date_field_names = Mock(return_value=['begin'])
# patching this way is evil as it is permanent and may affect proceeding tests.
# Maybe this can be done better (with patch method?)


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
        self.assertEqual(current_count, initial_count,
                         'There should be no reservation objects added to the database')


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
        self.assertEqual(current_count, initial_count,
                         'There should be no reservation objects added to the database')


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


class TimeIntervalValidatorTest(TestCase):

    def setup_and_patch_5_days(at_least_at_most):
        '''
        This method is a hack and is meant to be called only as decorator of other methods in this class.

        This uses python language definition as follows:
            when class is constructed, class body is executed - by the time methods in this class are not bound,
            so this method will be just a function - and we use this function to decorate other methods.
        '''

        if at_least_at_most == 'at_least':
            at_least_at_most = TimeIntervalValidator.NOT_SOONER
        elif at_least_at_most == 'at_most':
            at_least_at_most = TimeIntervalValidator.NOT_LATER
        else:
            raise ValueError('please supply "at_least" or "at_most" string as parameter')

        def actual_decorator(method):
            def new_method(self):
                self.reservation = Mock()
                self.validator = TimeIntervalValidator.objects.create(
                    time_unit='day',
                    time_value=5,
                    interval_type=at_least_at_most)
                TimeIntervalValidator._get_date_field_names = Mock(return_value=['start', 'end'])

                with patch('kitabu.models.validators.now') as dtmock:
                    dtmock.return_value = datetime(2000, 1, 1)

                    method(self)
            return new_method
        return actual_decorator

    @setup_and_patch_5_days('at_most')
    def test_today_is_ok(self):
        self.reservation.start = datetime(2000, 1, 1)
        self.reservation.end = datetime(2000, 1, 1)

        self.validator.validate(self.reservation)

    @setup_and_patch_5_days('at_most')
    def test_soon_enough(self):
        self.reservation.start = datetime(2000, 1, 3)
        self.reservation.end = datetime(2000, 1, 3)

        self.validator.validate(self.reservation)

    @setup_and_patch_5_days('at_most')
    def test_past_is_ok(self):
        self.reservation.start = datetime(1999, 4, 1)
        self.reservation.end = datetime(1999, 5, 1)

        self.validator.validate(self.reservation)

    @setup_and_patch_5_days('at_most')
    def test_almost_too_late(self):
        self.reservation.start = datetime(2000, 1, 5, 23, 59)
        self.reservation.end = datetime(2000, 1, 5, 23, 59)

        self.validator.validate(self.reservation)

    @setup_and_patch_5_days('at_most')
    def test_as_late_as_it_gets(self):
        self.reservation.start = datetime(2000, 1, 6, 0, 0)
        self.reservation.end = datetime(2000, 1, 6, 0, 0)

        self.validator.validate(self.reservation)

    @setup_and_patch_5_days('at_most')
    def test_much_later_is_ok(self):
        self.reservation.start = datetime(2000, 1, 16, 0, 0)
        self.reservation.end = datetime(2000, 1, 26, 0, 0)

        with self.assertRaises(ValidationError):
            self.validator.validate(self.reservation)

    @setup_and_patch_5_days('at_least')
    def test_today_is_too_soon(self):
        self.reservation.start = datetime(2000, 1, 1)
        self.reservation.end = datetime(2000, 1, 1)

        with self.assertRaises(ValidationError):
            self.validator.validate(self.reservation)

    @setup_and_patch_5_days('at_least')
    def test_too_soon(self):
        self.reservation.start = datetime(2000, 1, 3)
        self.reservation.end = datetime(2000, 1, 3)

        with self.assertRaises(ValidationError):
            self.validator.validate(self.reservation)

    @setup_and_patch_5_days('at_least')
    def test_past_is_too_soon(self):
        self.reservation.start = datetime(1999, 4, 1)
        self.reservation.end = datetime(1999, 5, 1)

        with self.assertRaises(ValidationError):
            self.validator.validate(self.reservation)

    @setup_and_patch_5_days('at_least')
    def test_slightly_too_soon(self):
        self.reservation.start = datetime(2000, 1, 5, 23, 59)
        self.reservation.end = datetime(2000, 1, 5, 23, 59)

        with self.assertRaises(ValidationError):
            self.validator.validate(self.reservation)

    @setup_and_patch_5_days('at_least')
    def test_as_soon_as_it_gets(self):
        self.reservation.start = datetime(2000, 1, 6, 0, 0)
        self.reservation.end = datetime(2000, 1, 6, 0, 0)

        self.validator.validate(self.reservation)

    @setup_and_patch_5_days('at_least')
    def test_much_later_is_much_too_late(self):
        self.reservation.start = datetime(2000, 1, 16, 0, 0)
        self.reservation.end = datetime(2000, 1, 26, 0, 0)

        self.validator.validate(self.reservation)

    def test_an_hour_too_soon_start(self):
        self.reservation = Mock()
        self.validator = TimeIntervalValidator.objects.create(
            time_unit='minute', time_value=15, interval_type=TimeIntervalValidator.NOT_SOONER)
        self.validator._get_date_field_names = Mock(return_value=['start'])

        with patch('kitabu.models.validators.now') as dtmock:
            dtmock.return_value = datetime(2000, 1, 1)

            self.reservation.start = datetime(1999, 12, 31, 23, 15)
            self.reservation.end = datetime(2000, 1, 26, 0, 0)

            with self.assertRaises(ValidationError):
                self.validator.validate(self.reservation)

    def test_a_quarter_too_soon_start(self):
        self.reservation = Mock()
        self.validator = TimeIntervalValidator.objects.create(
            time_unit='minute', time_value=45, interval_type=TimeIntervalValidator.NOT_SOONER)
        TimeIntervalValidator._get_date_field_names = Mock(return_value=['start'])

        with patch('kitabu.models.validators.now') as dtmock:
            dtmock.return_value = datetime(2000, 1, 1)

            self.reservation.start = datetime(2000, 1, 1, 0, 30)

            with self.assertRaises(ValidationError):
                self.validator.validate(self.reservation)

    def test_just_in_time(self):
        self.reservation = Mock()
        self.validator = TimeIntervalValidator.objects.create(
            time_unit='minute', time_value=30, interval_type=TimeIntervalValidator.NOT_SOONER)
        TimeIntervalValidator._get_date_field_names = Mock(return_value=['start'])

        with patch('kitabu.models.validators.now') as dtmock:
            dtmock.return_value = datetime(2000, 1, 1)

            self.reservation.start = datetime(2000, 1, 1, 0, 30)

            self.validator.validate(self.reservation)


class NotSoonerThanValidatorTest(TestCase):

    def test_with_begin_field(self):
        validator = WithinPeriodValidator.objects.create()
        Period.objects.create(start=datetime(2000, 1, 2), validator=validator)
        WithinPeriodValidator._get_date_field_names = Mock(return_value=['begin'])
        reservation = Mock()

        reservation.begin = datetime(2000, 1, 2)
        validator.validate(reservation)

        with self.assertRaises(ValidationError):
            reservation.begin = datetime(2000, 1, 1)
            validator.validate(reservation)

    def test_with_start_end_fields(self):
        validator = WithinPeriodValidator.objects.create()
        Period.objects.create(start=datetime(2000, 1, 2), validator=validator)
        WithinPeriodValidator._get_date_field_names = Mock(return_value=['start', 'end'])
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
        validator = WithinPeriodValidator.objects.create()
        Period.objects.create(end=datetime(2000, 1, 2), validator=validator)
        WithinPeriodValidator._get_date_field_names = Mock(return_value=['begin'])
        reservation = Mock()

        reservation.begin = datetime(2000, 1, 2)
        validator.validate(reservation)

        with self.assertRaises(ValidationError):
            reservation.begin = datetime(2000, 1, 3)
            validator.validate(reservation)

    def test_with_start_end_fields(self):
        validator = WithinPeriodValidator.objects.create()
        Period.objects.create(end=datetime(2000, 1, 2), validator=validator)
        WithinPeriodValidator._get_date_field_names = Mock(return_value=['start', 'end'])
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
        validator = WithinPeriodValidator.objects.create()
        Period.objects.create(start=datetime(2000, 1, 2), end=datetime(2000, 1, 4), validator=validator)
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
        validator = WithinPeriodValidator.objects.create()
        Period.objects.create(start=datetime(2000, 1, 2), end=datetime(2000, 1, 4), validator=validator)
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


class WithinOneOfPeriodsTest(TestCase):

    def test_with_start_end_fields(self):
        validator = WithinPeriodValidator.objects.create()
        Period.objects.create(validator=validator,
                              start=datetime(2000, 1, 2),
                              end=datetime(2000, 1, 4))
        Period.objects.create(validator=validator,
                              start=datetime(2000, 2, 2),
                              end=datetime(2000, 2, 4))

        WithinPeriodValidator._get_date_field_names = Mock(return_value=['start', 'end'])
        reservation = Mock()

        reservation.start = datetime(2000, 1, 2)
        reservation.end = datetime(2000, 1, 4)

        validator.validate(reservation)

        reservation.start = datetime(2000, 1, 3)
        reservation.end = datetime(2000, 1, 1)

        with self.assertRaises(ValidationError):
            validator.validate(reservation)

        reservation.start = datetime(2000, 2, 2)
        reservation.end = datetime(2000, 1, 4)

        with self.assertRaises(ValidationError):
            validator.validate(reservation)

        reservation.start = datetime(2000, 1, 1, 16)
        reservation.end = datetime(2000, 1, 2)

        with self.assertRaises(ValidationError):
            validator.validate(reservation)

        reservation.start = datetime(2000, 1, 3)
        reservation.end = datetime(2000, 2, 3)

        with self.assertRaises(ValidationError):
            validator.validate(reservation)

        reservation.start = datetime(2000, 1, 6)
        reservation.end = datetime(2000, 2, 1)

        with self.assertRaises(ValidationError):
            validator.validate(reservation)

        reservation.start = datetime(2000, 1, 1)
        reservation.end = datetime(2000, 2, 14)

        with self.assertRaises(ValidationError):
            validator.validate(reservation)

        reservation.start = datetime(2000, 2, 3)
        reservation.end = datetime(2001, 1, 2)

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
        hours = [1, 1, 1, 0, 0, 0, 0, 1, 1, 1, 1, 1, 0, 0, 0, 1, 1, 1, 1, 1, 0, 0, 1, 1]

        self.validator = GivenHoursAndWeekdaysValidator.create_from_bitlists({
                                                                              'monday': hours,
                                                                              'tuesday': hours,
                                                                              'wednesday': [0] * 24,
                                                                              'thursday': hours,
                                                                              'friday': hours,
                                                                              'saturday': [0] * 24,
                                                                              'sunday': hours
                                                                              })

        self.reservation = Mock()

    def test_valid_hours_one_day_difference(self):
        #monday - tuesday
        self.reservation.start = datetime(2012, 11, 26, 22, 15)
        self.reservation.end = datetime(2012, 11, 27, 2, 45)
        self.validator.validate(self.reservation)

    def test_valid_hours_same_day(self):
        #monday
        self.reservation.start = datetime(2012, 11, 26, 8, 15)
        self.reservation.end = datetime(2012, 11, 26, 10, 45)
        self.validator.validate(self.reservation)

    def test_valid_hours_not_the_same_week(self):
        #sunday - monday
        self.reservation.start = datetime(2012, 11, 25, 22, 15)
        self.reservation.end = datetime(2012, 11, 26, 2, 45)
        self.validator.validate(self.reservation)

    def test_invalid_hours_one_day_difference(self):
        #monday - tuesday
        self.reservation.start = datetime(2012, 11, 26, 21, 15)
        self.reservation.end = datetime(2012, 11, 27, 2, 45)
        with self.assertRaises(ValidationError):
            self.validator.validate(self.reservation)

    def test_invalid_hours_same_day(self):
        #monday
        self.reservation.start = datetime(2012, 11, 26, 11, 15)
        self.reservation.end = datetime(2012, 11, 26, 13, 45)
        with self.assertRaises(ValidationError):
            self.validator.validate(self.reservation)

    def test_invalid_hours_not_the_same_week(self):
        #sunday - monday
        self.reservation.start = datetime(2012, 11, 25, 22, 15)
        self.reservation.end = datetime(2012, 11, 26, 4, 45)
        with self.assertRaises(ValidationError):
            self.validator.validate(self.reservation)


class MaxDurationValidatorTest(TestCase):
    def setUp(self):
        self.two_hours_validator = MaxDurationValidator.objects.create(max_duration_in_seconds=2 * 3600)
        self.two_days_and_one_hour_validator = MaxDurationValidator.objects.create(
                                                                        max_duration_in_seconds=2 * 3600 * 24 + 3600)
        self.reservation = Mock()

    def test_two_hours(self):
        self.reservation.start = datetime(2012, 10, 10, 10, 15)
        self.reservation.end = datetime(2012, 10, 10, 12, 15)
        self.two_hours_validator.validate(self.reservation)

    def test_two_hours_and_one_second(self):
        self.reservation.start = datetime(2012, 10, 10, 10, 15)
        self.reservation.end = datetime(2012, 10, 10, 12, 16)
        with self.assertRaises(ValidationError):
            self.two_hours_validator.validate(self.reservation)

    def test_two_days_and_one_hour(self):
        self.reservation.start = datetime(2012, 10, 10, 12, 15)
        self.reservation.end = datetime(2012, 10, 12, 13, 15)
        self.two_days_and_one_hour_validator.validate(self.reservation)

    def test_two_days_one_hour_and_one_second(self):
        self.reservation.start = datetime(2012, 10, 10, 12, 15)
        self.reservation.end = datetime(2012, 10, 12, 13, 16)
        with self.assertRaises(ValidationError):
            self.two_days_and_one_hour_validator.validate(self.reservation)
