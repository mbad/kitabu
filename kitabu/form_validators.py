from django.core.exceptions import ValidationError
import time


class BaseValidator(object):
    def __init__(self, message=u'Field error'):
        self.message = message

    def __call__(self, value):
        if not self.validate(value):
            raise ValidationError(self.message)


class FullSecondValidator(BaseValidator):
    def __init__(self, interval=1, *args, **kwargs):
        super(FullSecondValidator, self).__init__(*args, **kwargs)
        self.interval = interval

    def validate(self, datetime):
        timestamp = int(time.mktime(datetime.timetuple()))
        return (timestamp % self.interval) == 0


class FullMinuteValidator(FullSecondValidator):
    def __init__(self, interval=1, *args, **kwargs):
        super(FullMinuteValidator, self).__init__(interval=interval * 60, *args, **kwargs)


class FullHourValidator(FullMinuteValidator):
    def __init__(self, interval=1, *args, **kwargs):
        super(FullHourValidator, self).__init__(interval=interval * 60, *args, **kwargs)


class FullDayValidator(FullHourValidator):
    def __init__(self, interval=1, *args, **kwargs):
        super(FullDayValidator, self).__init__(interval=interval * 24, *args, **kwargs)
