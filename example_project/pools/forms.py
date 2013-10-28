from django import forms

from datetime import timedelta

from kitabu.search.reservations import SingleSubjectManagerReservationSearch

from lanes.models import LaneReservation
from spa.forms import SearchForm, PeriodForm


class PoolReservationsSearchForm(SearchForm, PeriodForm):
    def search(self, subject_manager):
        search = SingleSubjectManagerReservationSearch(reservation_model=LaneReservation,
                                                       subject_manager=subject_manager)
        return search.search(self.cleaned_data['start'], self.cleaned_data['end'])


class ClusterSearchForm(SearchForm, PeriodForm):
    required_size = forms.fields.IntegerField(min_value=1)


class PeriodSearchForm(SearchForm, PeriodForm):
    required_size = forms.fields.IntegerField(min_value=1)
    minutes = forms.fields.IntegerField(min_value=1, initial=60)

    def clean(self):
        cleaned_data = super(PeriodSearchForm, self).clean()
        cleaned_data['required_duration'] = timedelta(0, cleaned_data['minutes'] * 60)
        del cleaned_data['minutes']
        return cleaned_data
