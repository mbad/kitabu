from django.core.exceptions import ValidationError


class BaseValidator(object):
    def __init__(self, message=u'Field error'):
        self.message = message

    def __call__(self, value):
        if not self.validate(value):
            raise ValidationError(self.message)

    def validate(self, value):
        raise NotImplementedError('Abstract method')


class FullTimeIntervalValidator(BaseValidator):
    def __init__(self, interval=1, *args, **kwargs):
        super(FullTimeIntervalValidator, self).__init__(*args, **kwargs)
        self.interval = interval

    def _validate_datetime(self, main_part, must_be_null_parts):
        for part in must_be_null_parts:
            if part != 0:
                return False

        return main_part % self.interval == 0


class FullSecondValidator(FullTimeIntervalValidator):
    def validate(self, datetime):
        return self._validate_datetime(datetime.second, [datetime.microsecond])


class FullMinuteValidator(FullTimeIntervalValidator):
    def validate(self, datetime):
        return self._validate_datetime(datetime.minute, [datetime.second, datetime.microsecond])


class FullHourValidator(FullTimeIntervalValidator):
    def validate(self, datetime):
        return self._validate_datetime(datetime.hour, [datetime.minute, datetime.second, datetime.microsecond])


class FullDayValidator(FullTimeIntervalValidator):
    def validate(self, datetime):
        return self._validate_datetime(datetime.day,
                                       [datetime.hour, datetime.minute, datetime.second, datetime.microsecond])
