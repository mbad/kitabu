#-*- coding=utf-8 -*-

from django.db import models


class ReservationValidator(models.Model):
    class Meta:
        app_label = 'kitabu'

    actual_instance_name = models.CharField(max_length=200)

    def validate(self, *args, **kwargs):
        actual_instance = self._get_actual_instance()
        return actual_instance._perform_validation(*args, **kwargs)

    def save(self, *args, **kwargs):
        self._set_actual_instance_name()
        return super(ReservationValidator, self).save(*args, **kwargs)

    # Private

    def _get_actual_instance(self):
        if self._is_subclass():
            return getattr(self, self.actual_instance_name)
        else:
            return self

    def _is_subclass(self):
        return hasattr(self, self.actual_instance_name)

    def _perform_validation(self, *args, **kwargs):
        raise NotImplementedError('Must be implemented in subclasses!')

    def _set_actual_instance_name(self):
        if not self.actual_instance_name:
            self.actual_instance_name = self._get_actual_instance_name()

    def _get_actual_instance_name(self):
        return self.__class__.__name__.lower()


class FullTimeValidator(ReservationValidator):
    class Meta:
        abstract = True

    interval = models.PositiveIntegerField()
    interval_type = models.PositiveIntegerField()

    interval_types_mapping = {
        'second': 0,
        'minute': 1,
        'hour': 2,
        'day': 3,
    }
    extraction_functions = {
        interval_types_mapping['second']: lambda d: {
            'main_part': d.second,
            'must_be_null_parts': [d.microsecond]
        },
        interval_types_mapping['minute']: lambda d: {
            'main_part': d.minute,
            'must_be_null_parts': [d.second, d.microsecond]
        },
        interval_types_mapping['hour']: lambda d: {
            'main_part': d.hour,
            'must_be_null_parts': [d.minute, d.second, d.microsecond]
        },
        interval_types_mapping['day']: lambda d: {
            'main_part': d.day,
            'must_be_null_parts': [d.hour, d.minute, d.second, d.microsecond]
        }
    }

    def _perform_validation(self, **kwargs):
        start = kwargs['start']
        args = self._extract_arguments_from_datetime(start)
        return self._validate_datetime(args['main_part'],
                                       args['must_be_null_parts'])

    def _extract_arguments_from_datetime(self, datetime):
        extraction_function = self._get_argument_extractor()
        return extraction_function(datetime)

    def _get_argument_extractor(self):
        return self.extraction_functions[self.interval_type]

    def _validate_datetime(self, main_part, must_be_null_parts):
        return self._validate_must_be_null_parts(must_be_null_parts) and self._validate_main_part(main_part)

    def _validate_must_be_null_parts(self, parts):
        for part in parts:
            if part != 0:
                return False

        return True

    def _validate_main_part(self, part):
        return part % self.interval == 0
