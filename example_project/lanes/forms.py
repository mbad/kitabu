from django import forms
from crispy_forms.layout import Div, Layout, HTML

from spa.forms import PostForm, SearchForm, PeriodForm, GetForm
from spa.settings import MAX_LANE_RESERVATIONS_NR


class LaneReservationForm(PeriodForm, PostForm):
    size = forms.IntegerField(min_value=1, initial=1)
    exclusive = forms.BooleanField(widget=forms.CheckboxInput, required=False)
    approved = forms.BooleanField(widget=forms.CheckboxInput, initial=True, required=False)

    submit_button_text = 'Reserve'

    def __init__(self, *args, **kwargs):
        super(LaneReservationForm, self).__init__(*args, **kwargs)
        self.helper.layout = Layout(Div(HTML('<h4>Reservation</h4>'), 'start', 'end', 'size', 'exclusive', 'approved',
                                        css_class='reservation-form')
                                    )


class AvailableLanesSearchForm(SearchForm, PeriodForm):
    pass


class LaneReservationsNrForm(GetForm):
    forms_nr = forms.ChoiceField(choices=map(lambda x: (x, x), range(1, MAX_LANE_RESERVATIONS_NR + 1)), required=False,
                                 label="")
    submit_button_text = 'Change'
