from datetime import datetime, time

from mock import Mock, patch

from django.test import TestCase

from kitabu.exceptions import (
    ReservationError,
    InvalidPeriod,
    TooManyReservations,
    ForbiddenHours
)

from kitabu.tests.models import (
    FullTimeValidator,
    StaticValidator,
    TimeIntervalValidator,
    WithinPeriodValidator,
    NotWithinPeriodValidator,
    PeriodsInWeekdaysValidator,
    MaxDurationValidator,
    MaxReservationsPerUserValidator,
    Room,
    Period,
    WithinDayPeriod,
    Table,
)


def MockWithoutId():
    mock = Mock()
    mock.id = None
    return mock


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
        with self.assertRaises(InvalidPeriod):
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
        with self.assertRaises(InvalidPeriod):
            self.room.reserve(start=start, end=end, size=1)

        current_count = self.room.reservations.count()
        self.assertEqual(current_count, initial_count,
                         'There should be no reservation objects added to the database')


class FullTimeValidatorTest(TestCase):

    def test_half_a_minute(self):
        reservation = MockWithoutId()
        validator = FullTimeValidator.objects.create(interval_type='second', interval=30)

        reservation.start = datetime(2000, 1, 1, 16, 40)
        reservation.end = datetime(2000, 1, 1, 16, 40)
        validator.validate(reservation)

        reservation.start = datetime(2000, 1, 1, 16, 40, 0, 0)
        validator.validate(reservation)

        reservation.start = datetime(2000, 1, 1, 16, 40, 30, 0)
        validator.validate(reservation)

        with self.assertRaises(InvalidPeriod):
            reservation.start = datetime(2000, 1, 1, 16, 40, 15)
            validator.validate(reservation)

        with self.assertRaises(InvalidPeriod):
            reservation.start = datetime(2000, 1, 1, 16, 40, 0, 1)
            validator.validate(reservation)

    def test_full_hour_zero_minures(self):
        reservation = MockWithoutId()
        validator = FullTimeValidator.objects.create(interval_type='minute', interval=0)

        reservation.start = datetime(2000, 1, 1, 16, 0)
        reservation.end = datetime(2000, 1, 1, 16, 0)
        validator.validate(reservation)

        with self.assertRaises(InvalidPeriod):
            reservation.start = datetime(2000, 1, 1, 16, 40, 0, 1)
            validator.validate(reservation)

        with self.assertRaises(InvalidPeriod):
            reservation.start = datetime(2000, 1, 1, 16, 0, 0, 1)
            validator.validate(reservation)

    def test_full_hour_60_minutes(self):
        reservation = MockWithoutId()

        validator = FullTimeValidator.objects.create(interval_type='minute', interval=60)

        reservation.start = datetime(2000, 1, 1, 16, 0)
        reservation.end = datetime(2000, 1, 1, 16, 0)
        validator.validate(reservation)

        with self.assertRaises(InvalidPeriod):
            reservation.start = datetime(2000, 1, 1, 16, 40, 0, 0)
            validator.validate(reservation)

        with self.assertRaises(InvalidPeriod):
            reservation.start = datetime(2000, 1, 1, 16, 0, 0, 1)
            validator.validate(reservation)

    def test_many_fields(self):
        reservation = MockWithoutId()
        validator = FullTimeValidator.objects.create(interval_type='hour', interval=2)

        reservation.start = reservation.end = datetime(2000, 1, 1, 16, 0)
        validator.validate(reservation)

        reservation.start = datetime(2000, 1, 1, 14, 0)
        reservation.end = datetime(2000, 1, 1, 16, 0)
        validator.validate(reservation)

        with self.assertRaises(InvalidPeriod):
            reservation.start = datetime(2000, 1, 1, 15, 0, 0, 0)
            reservation.end = datetime(2000, 1, 1, 16, 0)
            validator.validate(reservation)

        with self.assertRaises(InvalidPeriod):
            reservation.start = datetime(2000, 1, 1, 16, 0, 0, 0)
            reservation.end = datetime(2000, 1, 1, 17, 0, 0, 0)
            validator.validate(reservation)

        with self.assertRaises(InvalidPeriod):
            reservation.start = datetime(2000, 1, 1, 15, 0, 0, 0)
            reservation.end = datetime(2000, 1, 1, 17, 0, 0, 0)
            validator.validate(reservation)


class StaticValidatorTest(TestCase):

    def test_failing_validator(self):
        reservation = MockWithoutId()
        validator = StaticValidator.objects.create(
            validator_function_absolute_name='kitabu.tests.validators.StaticValidatorTest.fail')

        with self.assertRaises(ReservationError):
            validator.validate(reservation)

    def test_passing_validator(self):
        reservation = MockWithoutId()
        validator = StaticValidator.objects.create(
            validator_function_absolute_name='kitabu.tests.validators.StaticValidatorTest.pass_')

        validator.validate(reservation)

    def test_fail_for_a_reason_validator(self):
        reservation = MockWithoutId()
        validator = StaticValidator.objects.create(
            validator_function_absolute_name='kitabu.tests.validators.StaticValidatorTest.fail_for_a_reason')

        reservation.reason = Mock(return_value=False)
        validator.validate(reservation)
        reservation.reason.assert_called_once_with()
        reservation.reason = Mock(return_value=True)
        with self.assertRaises(ReservationError):
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
        raise ReservationError()

    @staticmethod
    def pass_(reservation):
        pass

    @staticmethod
    def fail_for_a_reason(reservation):
        if hasattr(reservation, 'reason'):
            if reservation.reason():
                raise ReservationError()


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
                self.reservation = MockWithoutId()
                self.validator = TimeIntervalValidator.objects.create(
                    time_unit='day',
                    time_value=5,
                    interval_type=at_least_at_most)

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

        with self.assertRaises(InvalidPeriod):
            self.validator.validate(self.reservation)

    @setup_and_patch_5_days('at_least')
    def test_today_is_too_soon(self):
        self.reservation.start = datetime(2000, 1, 1)
        self.reservation.end = datetime(2000, 1, 1)

        with self.assertRaises(InvalidPeriod):
            self.validator.validate(self.reservation)

    @setup_and_patch_5_days('at_least')
    def test_too_soon(self):
        self.reservation.start = datetime(2000, 1, 3)
        self.reservation.end = datetime(2000, 1, 3)

        with self.assertRaises(InvalidPeriod):
            self.validator.validate(self.reservation)

    @setup_and_patch_5_days('at_most')
    def test_end_can_normally_be_later(self):
        self.reservation.start = datetime(2000, 1, 3)
        self.reservation.end = datetime(2000, 1, 30)

        self.validator.validate(self.reservation)

    @setup_and_patch_5_days('at_most')
    def test_end_cannot_be_later(self):
        self.validator.check_end = True
        self.validator.save()
        self.reservation.start = datetime(2000, 1, 3)
        self.reservation.end = datetime(2000, 1, 30)

        with self.assertRaises(InvalidPeriod):
            self.validator.validate(self.reservation)

    @setup_and_patch_5_days('at_least')
    def test_past_is_too_soon(self):
        self.reservation.start = datetime(1999, 4, 1)
        self.reservation.end = datetime(1999, 5, 1)

        with self.assertRaises(InvalidPeriod):
            self.validator.validate(self.reservation)

    @setup_and_patch_5_days('at_least')
    def test_slightly_too_soon(self):
        self.reservation.start = datetime(2000, 1, 5, 23, 59)
        self.reservation.end = datetime(2000, 1, 5, 23, 59)

        with self.assertRaises(InvalidPeriod):
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
        self.reservation = MockWithoutId()
        self.validator = TimeIntervalValidator.objects.create(
            time_unit='minute', time_value=15, interval_type=TimeIntervalValidator.NOT_SOONER)

        with patch('kitabu.models.validators.now') as dtmock:
            dtmock.return_value = datetime(2000, 1, 1)

            self.reservation.start = datetime(1999, 12, 31, 23, 15)
            self.reservation.end = datetime(2000, 1, 26, 0, 0)

            with self.assertRaises(InvalidPeriod):
                self.validator.validate(self.reservation)

    def test_a_quarter_too_soon_start(self):
        self.reservation = MockWithoutId()
        self.validator = TimeIntervalValidator.objects.create(
            time_unit='minute', time_value=45, interval_type=TimeIntervalValidator.NOT_SOONER)

        with patch('kitabu.models.validators.now') as dtmock:
            dtmock.return_value = datetime(2000, 1, 1)

            self.reservation.start = datetime(2000, 1, 1, 0, 30)
            self.reservation.end = datetime(2000, 1, 1, 0, 30)

            with self.assertRaises(InvalidPeriod):
                self.validator.validate(self.reservation)

    def test_just_in_time(self):
        self.reservation = MockWithoutId()
        self.validator = TimeIntervalValidator.objects.create(
            time_unit='minute', time_value=30, interval_type=TimeIntervalValidator.NOT_SOONER)

        with patch('kitabu.models.validators.now') as dtmock:
            dtmock.return_value = datetime(2000, 1, 1)

            self.reservation.start = datetime(2000, 1, 1, 0, 30)
            self.reservation.end = datetime(2000, 1, 1, 0, 30)

            self.validator.validate(self.reservation)


class NotSoonerThanValidatorTest(TestCase):

    def test_not_sooner_than(self):
        validator = WithinPeriodValidator.objects.create()
        Period.objects.create(start=datetime(2000, 1, 2), validator=validator)
        reservation = MockWithoutId()

        reservation.start = datetime(2000, 1, 1)
        reservation.end = datetime(2000, 1, 1)

        with self.assertRaises(InvalidPeriod):
            validator.validate(reservation)

        reservation.start = datetime(2000, 1, 3)
        reservation.end = datetime(2000, 1, 1)

        with self.assertRaises(InvalidPeriod):
            validator.validate(reservation)

        reservation.start = datetime(2000, 1, 1)
        reservation.end = datetime(2000, 1, 4)

        with self.assertRaises(InvalidPeriod):
            validator.validate(reservation)

        reservation.start = datetime(2000, 1, 1, 16)
        reservation.end = datetime(2000, 1, 4)


class NotLaterThanValidatorTest(TestCase):

    def test_not_later_than(self):
        validator = WithinPeriodValidator.objects.create()
        Period.objects.create(end=datetime(2000, 1, 2), validator=validator)
        reservation = MockWithoutId()

        reservation.start = datetime(2000, 1, 1)
        reservation.end = datetime(2000, 1, 3)

        with self.assertRaises(InvalidPeriod):
            validator.validate(reservation)

        reservation.start = datetime(2000, 1, 3)
        reservation.end = datetime(2000, 1, 1)

        with self.assertRaises(InvalidPeriod):
            validator.validate(reservation)

        reservation.start = datetime(2000, 1, 3)
        reservation.end = datetime(2000, 1, 4)

        with self.assertRaises(InvalidPeriod):
            validator.validate(reservation)

        reservation.start = datetime(2000, 1, 1, 16)
        reservation.end = datetime(2000, 1, 1)
        validator.validate(reservation)


class WithinPeriodTest(TestCase):

    def test_within_period(self):
        validator = WithinPeriodValidator.objects.create()
        Period.objects.create(start=datetime(2000, 1, 2), end=datetime(2000, 1, 4), validator=validator)
        reservation = MockWithoutId()

        reservation.start = datetime(2000, 1, 2)
        reservation.end = datetime(2000, 1, 4)

        validator.validate(reservation)

        reservation.start = datetime(2000, 1, 3)
        reservation.end = datetime(2000, 1, 1)

        with self.assertRaises(InvalidPeriod):
            validator.validate(reservation)

        reservation.start = datetime(2000, 1, 4)
        reservation.end = datetime(2000, 1, 3)

        validator.validate(reservation)

        reservation.start = datetime(2000, 1, 1, 16)
        reservation.end = datetime(2000, 1, 2)

        with self.assertRaises(InvalidPeriod):
            validator.validate(reservation)

        reservation.start = datetime(2000, 1, 3)
        reservation.end = datetime(2000, 1, 1)

        with self.assertRaises(InvalidPeriod):
            validator.validate(reservation)

        reservation.start = datetime(2000, 1, 6)
        reservation.end = datetime(2000, 1, 4)

        with self.assertRaises(InvalidPeriod):
            validator.validate(reservation)

        reservation.start = datetime(2000, 1, 1)
        reservation.end = datetime(2000, 1, 14)

        with self.assertRaises(InvalidPeriod):
            validator.validate(reservation)

        reservation.start = datetime(2001, 1, 1)
        reservation.end = datetime(2001, 1, 14)

        with self.assertRaises(InvalidPeriod):
            validator.validate(reservation)


class WithinOneOfPeriodsTest(TestCase):

    def test_within_one_of_periods(self):
        validator = WithinPeriodValidator.objects.create()
        Period.objects.create(validator=validator,
                              start=datetime(2000, 1, 2),
                              end=datetime(2000, 1, 4))
        Period.objects.create(validator=validator,
                              start=datetime(2000, 2, 2),
                              end=datetime(2000, 2, 4))

        reservation = MockWithoutId()

        reservation.start = datetime(2000, 1, 2)
        reservation.end = datetime(2000, 1, 4)

        validator.validate(reservation)

        reservation.start = datetime(2000, 1, 3)
        reservation.end = datetime(2000, 1, 1)

        with self.assertRaises(InvalidPeriod):
            validator.validate(reservation)

        reservation.start = datetime(2000, 2, 2)
        reservation.end = datetime(2000, 1, 4)

        with self.assertRaises(InvalidPeriod):
            validator.validate(reservation)

        reservation.start = datetime(2000, 1, 1, 16)
        reservation.end = datetime(2000, 1, 2)

        with self.assertRaises(InvalidPeriod):
            validator.validate(reservation)

        reservation.start = datetime(2000, 1, 3)
        reservation.end = datetime(2000, 2, 3)

        with self.assertRaises(InvalidPeriod):
            validator.validate(reservation)

        reservation.start = datetime(2000, 1, 6)
        reservation.end = datetime(2000, 2, 1)

        with self.assertRaises(InvalidPeriod):
            validator.validate(reservation)

        reservation.start = datetime(2000, 1, 1)
        reservation.end = datetime(2000, 2, 14)

        with self.assertRaises(InvalidPeriod):
            validator.validate(reservation)

        reservation.start = datetime(2000, 2, 3)
        reservation.end = datetime(2001, 1, 2)

        with self.assertRaises(InvalidPeriod):
            validator.validate(reservation)


class NotWithinPeriodTest(TestCase):

    def test_with_start_end_fields(self):
        validator = NotWithinPeriodValidator.objects.create(start=datetime(2000, 1, 2),
                                                            end=datetime(2000, 1, 4))
        reservation = MockWithoutId()

        reservation.start = datetime(2000, 1, 2)
        reservation.end = datetime(2000, 1, 4)

        with self.assertRaises(InvalidPeriod):
            validator.validate(reservation)

        reservation.start = datetime(2000, 1, 1)
        reservation.end = datetime(2000, 1, 3)

        with self.assertRaises(InvalidPeriod):
            validator.validate(reservation)

        reservation.start = datetime(2000, 1, 3)
        reservation.end = datetime(2000, 1, 4)

        with self.assertRaises(InvalidPeriod):
            validator.validate(reservation)

        reservation.start = datetime(2000, 1, 1, 16)
        reservation.end = datetime(2000, 1, 2)

        with self.assertRaises(InvalidPeriod):
            validator.validate(reservation)

        reservation.start = datetime(2000, 1, 1)
        reservation.end = datetime(2000, 1, 3)

        with self.assertRaises(InvalidPeriod):
            validator.validate(reservation)

        reservation.start = datetime(2000, 1, 4)
        reservation.end = datetime(2000, 1, 6)

        with self.assertRaises(InvalidPeriod):
            validator.validate(reservation)

        reservation.start = datetime(2000, 1, 1)
        reservation.end = datetime(2000, 1, 14)

        with self.assertRaises(InvalidPeriod):
            validator.validate(reservation)

        reservation.start = datetime(2001, 1, 1)
        reservation.end = datetime(2001, 1, 14)

        validator.validate(reservation)


class PeriodsInWeekdaysTest(TestCase):
    def setUp(self):
        self.validator = PeriodsInWeekdaysValidator.objects.create()
        self.almost_whole_week_validator = PeriodsInWeekdaysValidator.objects.create()
        self.overlapping_periods_validator = PeriodsInWeekdaysValidator.objects.create()

        period_params_list = [
            (0, {'start': time(12, 0), 'end': time(14, 0)}),
            (1, {'start': time(15, 0), 'end': time(17, 0)}),

            # Wednesday
            (2, {'start': time(12, 0)}),
            (3, {}),
            (4, {'end': time(14, 0)}),
        ]
        almost_whole_week_params_list = [
            (0, {}),
            (1, {}),
            (2, {}),

            # Thursday
            (3, {'end': time(10, 0)}),
            (3, {'start': time(20, 0)}),
            (4, {}),
            (5, {}),
            (6, {}),
        ]
        # Sunday: 10-12, 14-16 (two periods)
        overlapping_periods_params_list = [
            (0, {}),
            (1, {}),
            (2, {}),
            (3, {}),
            (4, {}),
            (5, {}),
            (6, {'start': time(10, 0), 'end': time(12, 0)}),
            (6, {'start': time(11, 30), 'end': time(13, 0)}),
            (6, {'start': time(11, 0), 'end': time(11, 30)}),
            (6, {'start': time(14, 0), 'end': time(15, 0)}),
            (6, {'start': time(15, 0), 'end': time(16, 0)}),
        ]

        for period_params in period_params_list:
            WithinDayPeriod.objects.create(weekday=period_params[0], validator=self.validator, **period_params[1])

        for period_params in almost_whole_week_params_list:
            WithinDayPeriod.objects.create(weekday=period_params[0], validator=self.almost_whole_week_validator,
                                           **period_params[1])

        for period_params in overlapping_periods_params_list:
            WithinDayPeriod.objects.create(weekday=period_params[0], validator=self.overlapping_periods_validator,
                                           **period_params[1])

        self.reservation = MockWithoutId()

    # Monday: 2013-03-18
    def test_validation_same_day(self):
        self.reservation.start = datetime(2013, 03, 18, 12, 00)
        self.reservation.end = datetime(2013, 03, 18, 14, 00)
        self.validator.validate(self.reservation)

        self.reservation.start = datetime(2013, 03, 18, 11, 59, 59)
        self.reservation.end = datetime(2013, 03, 18, 14, 00)
        with self.assertRaises(ForbiddenHours):
            self.validator.validate(self.reservation)

        self.reservation.start = datetime(2013, 03, 18, 12, 00)
        self.reservation.end = datetime(2013, 03, 18, 14, 00, 01)
        with self.assertRaises(ForbiddenHours):
            self.validator.validate(self.reservation)

    # Wednesday: 2013-03-20
    def test_validation_more_days(self):
        self.reservation.start = datetime(2013, 03, 20, 12, 00)
        self.reservation.end = datetime(2013, 03, 22, 14, 00)
        self.validator.validate(self.reservation)

        self.reservation.start = datetime(2013, 03, 20, 11, 59, 59)
        self.reservation.end = datetime(2013, 03, 22, 14, 00)
        with self.assertRaises(ForbiddenHours):
            self.validator.validate(self.reservation)

        self.reservation.start = datetime(2013, 03, 20, 12, 00)
        self.reservation.end = datetime(2013, 03, 22, 14, 00, 01)
        with self.assertRaises(ForbiddenHours):
            self.validator.validate(self.reservation)

    # Thursday: 2013-03-21, next thursday: 2013-03-28
    def test_validation_almost_whole_week(self):
        self.reservation.start = datetime(2013, 03, 21, 20, 00)
        self.reservation.end = datetime(2013, 03, 28, 10, 00)
        self.almost_whole_week_validator.validate(self.reservation)

        self.reservation.start = datetime(2013, 03, 21, 19, 59, 59)
        self.reservation.end = datetime(2013, 03, 28, 10, 00)
        with self.assertRaises(ForbiddenHours):
            self.almost_whole_week_validator.validate(self.reservation)

        self.reservation.start = datetime(2013, 03, 21, 20, 00)
        self.reservation.end = datetime(2013, 03, 28, 10, 00, 01)
        with self.assertRaises(ForbiddenHours):
            self.almost_whole_week_validator.validate(self.reservation)

    # Thursday: 2013-03-21, next thursday: 2013-03-28
    def test_validation_more_then_week(self):
        self.reservation.start = datetime(2013, 03, 21, 20, 00)
        self.reservation.end = datetime(2013, 03, 29, 10, 00)
        with self.assertRaises(ForbiddenHours):
            self.almost_whole_week_validator.validate(self.reservation)

    # Sunday: 2013-11-17
    def test_validation_for_more_periods_in_the_same_day(self):
        self.reservation.start = datetime(2013, 11, 17, 10, 00)
        self.reservation.end = datetime(2013, 11, 17, 13, 00)
        self.overlapping_periods_validator.validate(self.reservation)

        self.reservation.start = datetime(2013, 11, 17, 14, 00)
        self.reservation.end = datetime(2013, 11, 17, 16, 00)
        self.overlapping_periods_validator.validate(self.reservation)

        self.reservation.start = datetime(2013, 11, 17, 10, 00)
        self.reservation.end = datetime(2013, 11, 17, 13, 00, 01)
        with self.assertRaises(ForbiddenHours):
            self.overlapping_periods_validator.validate(self.reservation)

        self.reservation.start = datetime(2013, 11, 17, 13, 59, 59)
        self.reservation.end = datetime(2013, 11, 17, 15, 00)
        with self.assertRaises(ForbiddenHours):
            self.overlapping_periods_validator.validate(self.reservation)


class MaxDurationValidatorTest(TestCase):
    def setUp(self):
        self.two_hours_validator = MaxDurationValidator.objects.create(max_duration_in_seconds=2 * 3600)
        self.two_days_and_one_hour_validator = MaxDurationValidator.objects.create(
            max_duration_in_seconds=2 * 3600 * 24 + 3600)
        self.reservation = MockWithoutId()

    def test_two_hours(self):
        self.reservation.start = datetime(2012, 10, 10, 10, 15)
        self.reservation.end = datetime(2012, 10, 10, 12, 15)
        self.two_hours_validator.validate(self.reservation)

    def test_two_hours_and_one_second(self):
        self.reservation.start = datetime(2012, 10, 10, 10, 15)
        self.reservation.end = datetime(2012, 10, 10, 12, 16)
        with self.assertRaises(InvalidPeriod):
            self.two_hours_validator.validate(self.reservation)

    def test_two_days_and_one_hour(self):
        self.reservation.start = datetime(2012, 10, 10, 12, 15)
        self.reservation.end = datetime(2012, 10, 12, 13, 15)
        self.two_days_and_one_hour_validator.validate(self.reservation)

    def test_two_days_one_hour_and_one_second(self):
        self.reservation.start = datetime(2012, 10, 10, 12, 15)
        self.reservation.end = datetime(2012, 10, 12, 13, 16)
        with self.assertRaises(InvalidPeriod):
            self.two_days_and_one_hour_validator.validate(self.reservation)


class MaxReservationsPerUserValidatorTest(TestCase):
    def setUp(self):
        self.user = "Family Guy"
        self.table = Table.objects.create()
        self.validator1_2 = MaxReservationsPerUserValidator.objects.create(
            max_reservations_on_current_subject=1,
            max_reservations_on_all_subjects=2)
        self.validator2_3 = MaxReservationsPerUserValidator.objects.create(
            max_reservations_on_current_subject=2,
            max_reservations_on_all_subjects=3)
        self.validator3_2 = MaxReservationsPerUserValidator.objects.create(
            max_reservations_on_current_subject=3,
            max_reservations_on_all_subjects=2)

    def test_first_reservation(self):
        with patch('kitabu.models.validators.now') as dtmock:
            dtmock.return_value = datetime(2000, 1, 1)
            table = Table.objects.create()
            table.validators.add(self.validator1_2)
            table.reserve(start=datetime(2000, 2, 1), end=datetime(2000, 2, 3), owner=self.user)

    def test_too_many_reservations_on_subject(self):
        with patch('kitabu.models.validators.now') as dtmock:
            validator = MaxReservationsPerUserValidator.objects.create(
                max_reservations_on_current_subject=1,
                max_reservations_on_all_subjects=0)
            dtmock.return_value = datetime(2000, 1, 1)
            table = Table.objects.create()
            table.validators.add(validator)
            table.reserve(start=datetime(2000, 2, 1), end=datetime(2000, 2, 3), owner=self.user)
            with self.assertRaises(TooManyReservations):
                table.reserve(start=datetime(2000, 3, 1), end=datetime(2000, 3, 3), owner=self.user)

    def test_too_many_reservations_on_subject_when_all_also_limited(self):
        with patch('kitabu.models.validators.now') as dtmock:
            dtmock.return_value = datetime(2000, 1, 1)
            table = Table.objects.create()
            table.validators.add(self.validator1_2)
            table.reserve(start=datetime(2000, 2, 1), end=datetime(2000, 2, 3), owner=self.user)
            with self.assertRaises(TooManyReservations):
                table.reserve(start=datetime(2000, 3, 1), end=datetime(2000, 3, 3), owner=self.user)

    def test_many_past_reservations_on_subject(self):
        with patch('kitabu.models.validators.now') as dtmock:
            dtmock.return_value = datetime(2000, 1, 1)
            table = Table.objects.create()
            table.validators.add(self.validator1_2)
            table.reserve(start=datetime(1996, 2, 1), end=datetime(1996, 2, 3), owner=self.user)
            table.reserve(start=datetime(1997, 2, 1), end=datetime(1997, 2, 3), owner=self.user)
            table.reserve(start=datetime(1998, 2, 1), end=datetime(1998, 2, 3), owner=self.user)
            table.reserve(start=datetime(1999, 2, 1), end=datetime(1999, 2, 3), owner=self.user)
            table.reserve(start=datetime(2000, 2, 1), end=datetime(2000, 2, 3), owner=self.user)

    def test_many_past_reservations_on_other_subjects(self):
        with patch('kitabu.models.validators.now') as dtmock:
            dtmock.return_value = datetime(2000, 1, 1)
            table = Table.objects.create()
            table.validators.add(self.validator1_2)
            Table.objects.create().reserve(start=datetime(1996, 2, 1), end=datetime(1996, 2, 3), owner=self.user)
            Table.objects.create().reserve(start=datetime(1997, 2, 1), end=datetime(1997, 2, 3), owner=self.user)
            Table.objects.create().reserve(start=datetime(1998, 2, 1), end=datetime(1998, 2, 3), owner=self.user)
            Table.objects.create().reserve(start=datetime(1999, 2, 1), end=datetime(1999, 2, 3), owner=self.user)
            table.reserve(start=datetime(2000, 2, 1), end=datetime(2000, 2, 3), owner=self.user)

    def test_many_reservations_on_other_subjects(self):
        with patch('kitabu.models.validators.now') as dtmock:
            dtmock.return_value = datetime(2000, 1, 1)
            validator = MaxReservationsPerUserValidator.objects.create(
                max_reservations_on_current_subject=2,
                max_reservations_on_all_subjects=0)
            table = Table.objects.create()
            table.validators.add(validator)
            for i in range(5):
                Table.objects.create().reserve(start=datetime(2000, 2, 1), end=datetime(2000, 2, 3), owner=self.user)
            table.reserve(start=datetime(2000, 2, 1), end=datetime(2000, 2, 3), owner=self.user)  # first reservation on the table
            table.reserve(start=datetime(2000, 2, 1), end=datetime(2000, 2, 3), owner=self.user)  # second reservation on the table
            with self.assertRaises(TooManyReservations):  # third reservation on the table is not possible
                table.reserve(start=datetime(2000, 2, 1), end=datetime(2000, 2, 3), owner=self.user)

    def test_too_many_reservations_on_other_subjects(self):
        with patch('kitabu.models.validators.now') as dtmock:
            dtmock.return_value = datetime(2000, 1, 1)
            validator = MaxReservationsPerUserValidator.objects.create(
                max_reservations_on_current_subject=3,
                max_reservations_on_all_subjects=5)
            table = Table.objects.create()
            table.validators.add(validator)
            table.reserve(start=datetime(2000, 2, 1), end=datetime(2000, 2, 3), owner=self.user)  # first reservation on the table
            table.reserve(start=datetime(2000, 2, 1), end=datetime(2000, 2, 3), owner=self.user)  # second reservation on the table
            for i in range(3):  # this gives 5 reservations all together
                Table.objects.create().reserve(start=datetime(2000, 2, 1), end=datetime(2000, 2, 3), owner=self.user)
            with self.assertRaises(TooManyReservations):
                # third reservation on the table is not possible because of other tables reservations
                table.reserve(start=datetime(2000, 2, 1), end=datetime(2000, 2, 3), owner=self.user)

    def test_too_many_reservations_on_other_subjects_current_unlimited(self):
        with patch('kitabu.models.validators.now') as dtmock:
            dtmock.return_value = datetime(2000, 1, 1)
            validator = MaxReservationsPerUserValidator.objects.create(
                max_reservations_on_current_subject=0,
                max_reservations_on_all_subjects=5)
            table = Table.objects.create()
            table.validators.add(validator)
            table.reserve(start=datetime(2000, 2, 1), end=datetime(2000, 2, 3), owner=self.user)  # first reservation on the table
            table.reserve(start=datetime(2000, 2, 1), end=datetime(2000, 2, 3), owner=self.user)  # second reservation on the table
            for i in range(3):  # this gives 5 reservations all together
                Table.objects.create().reserve(start=datetime(2000, 2, 1), end=datetime(2000, 2, 3), owner=self.user)
            with self.assertRaises(TooManyReservations):
                # third reservation on the table is not possible because of other tables reservations
                table.reserve(start=datetime(2000, 2, 1), end=datetime(2000, 2, 3), owner=self.user)
