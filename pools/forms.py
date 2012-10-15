from django import forms

from kitabu.forms.availability import (
    FiniteAvailabilityForm,
    OneClusterAvailabilityFormMixin,
    ClusterFiniteAvailabilityForm,
)
from kitabu.search.reservations import SingleSubjectManagerReservationSearch

from lanes.models import Lane, LaneReservation
from pools.models import Pool
from spa.forms import SearchForm


class AvailableLanesSearchForm(
        SearchForm,
        OneClusterAvailabilityFormMixin,
        FiniteAvailabilityForm.on_model(Lane)):
    pass


class PoolReservationsSearchForm(SearchForm):
    start = forms.DateTimeField()
    end = forms.DateTimeField()

    def search(self, subject_manager):
        search = SingleSubjectManagerReservationSearch(reservation_model=LaneReservation,
                                                       subject_manager=subject_manager)
        return search.search(self.cleaned_data['start'], self.cleaned_data['end'])


class ClusterSearchForm(
    SearchForm,
    ClusterFiniteAvailabilityForm.on_models(Lane, Pool, 'subjects')
):
    pass
