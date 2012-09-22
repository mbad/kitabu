from django import forms
from django.forms import ValidationError
from django.forms.util import ErrorList

from kitabu.exceptions import SizeExceeded
from kitabu.forms import KitabuPostForm


class BaseReservationForm(KitabuPostForm):
    start = forms.DateTimeField(widget=forms.DateTimeInput(attrs={'class': 'kitabu-datetime-field'}))
    end = forms.DateTimeField(widget=forms.DateTimeInput(attrs={'class': 'kitabu-datetime-field'}))

    submit_button_text = 'Reserve'

    def clean(self):
        if 'start' in self.cleaned_data and 'end' in self.cleaned_data:
            start = self.cleaned_data['start']
            end = self.cleaned_data['end']
            if not end > start:
                raise ValidationError('Reservation must end after it begins')
        return super(BaseReservationForm, self).clean()


class ReservationWithSizeForm(BaseReservationForm):
    size = forms.IntegerField(min_value=1)

    def make_reservation(self, subject, **kwargs):
        reservation_params = self.cleaned_data
        reservation_params.update(kwargs)
        try:
            return subject.reserve(**reservation_params)
        except SizeExceeded:
            if "__all__" not in self._errors:
                self._errors["__all__"] = ErrorList()
            self.errors['__all__'].append("Too many reservations")
            return None
