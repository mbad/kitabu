from django import forms
from django.forms import ValidationError
from django.forms.util import ErrorList

from kitabu.exceptions import SizeExceeded


class BaseReservationForm(forms.Form):
    start = forms.SplitDateTimeField()
    end = forms.SplitDateTimeField()

    def clean(self):
        if 'start' in self.cleaned_data and 'end' in self.cleaned_data:
            start = self.cleaned_data['start']
            end = self.cleaned_data['end']
            if not end > start:
                raise ValidationError(
                        'Reservation must end after it begins')
        return super(BaseReservationForm, self).clean()


class ReservationWithSizeForm(forms.Form):
    size = forms.IntegerField(min_value=1)

    def make_reservation(self, subject, **kwargs):
        if not self.is_valid():
            return None
        reservation_params = self.cleaned_data
        reservation_params.update(kwargs)
        try:
            return subject.reserve(**reservation_params)
        except SizeExceeded:
            if "__all__" not in self._errors:
                self._errors["__all__"] = ErrorList()
            self.errors['__all__'].append("Too many reservations")
            return None
