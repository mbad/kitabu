from django import forms

from spa.forms import PostForm, SearchForm, PeriodForm


class LaneReservationForm(PeriodForm, PostForm):
    size = forms.IntegerField(min_value=1)
    submit_button_text = 'Reserve'


class AvailableLanesSearchForm(SearchForm, PeriodForm):
    pass
