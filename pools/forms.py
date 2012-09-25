from kitabu.forms.availability import (
    FiniteAvailabilityForm,
    OneClusterAvailabilityFormMixin,
    ClusterFiniteAvailabilityForm,
)
from kitabu.forms.reservation_search import SingleClusterReservationSearchMixin, BaseReservationSearchForm

from lanes.models import Lane, LaneReservation
from pools.models import Pool
from spa.forms import SearchForm


class AvailableLanesSearchForm(
        SearchForm,
        OneClusterAvailabilityFormMixin,
        FiniteAvailabilityForm.on_model(Lane)):
    pass


class PoolReservationsSearchForm(
        SingleClusterReservationSearchMixin,
        BaseReservationSearchForm,
        SearchForm):
    reservation_model = LaneReservation


class ClusterSearchForm(
    SearchForm,
    ClusterFiniteAvailabilityForm.on_models(Lane, Pool, 'subjects')
):
    pass
