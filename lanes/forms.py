from kitabu.forms.reservation import ReservationWithSizeForm
from kitabu.forms.availability import ExclusiveAvailabilityForm
from kitabu.forms.validators import FullHourValidator, FullMinuteValidator

from models import LaneReservation, Lane


class LaneReservationForm(ReservationWithSizeForm):
    reservation_model = LaneReservation

    def clean_start(self):
        if 'start' in self.cleaned_data:
            FullHourValidator(message='Only full hours allowed')(self.cleaned_data['start'])

    def clean_end(self):
        if 'end' in self.cleaned_data:
            FullMinuteValidator(message='Only full minutes allowed')(self.cleaned_data['end'])


class AvailableLanesSearchForm(ExclusiveAvailabilityForm.on_model(Lane)):
    pass
