from kitabu.forms.reservation import ReservationWithSizeForm
from kitabu.forms.availability import ExclusiveAvailabilityForm

from models import LaneReservation, Lane

from spa.forms import PostForm, SearchForm


class LaneReservationForm(ReservationWithSizeForm, PostForm):
    reservation_model = LaneReservation

    submit_button_text = 'Reserve'


class AvailableLanesSearchForm(ExclusiveAvailabilityForm.on_model(Lane), SearchForm):
    pass
