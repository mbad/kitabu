from kitabu.forms.reservation import ReservationWithSizeForm

from models import LaneReservation

from spa.forms import PostForm, SearchForm, PeriodForm


class LaneReservationForm(ReservationWithSizeForm, PostForm):
    reservation_model = LaneReservation

    submit_button_text = 'Reserve'


class AvailableLanesSearchForm(SearchForm, PeriodForm):
    pass
