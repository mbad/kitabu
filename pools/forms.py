from kitabu.availability_forms import FiniteAvailabilityForm, OneClusterAvailabilityFormMixin
from kitabu.reservation_search_forms import SingleClusterReservationSearchMixin, BaseReservationSearchForm

from lanes.models import Lane, LaneReservation


class AvailableLanesSearchForm(
        OneClusterAvailabilityFormMixin,
        FiniteAvailabilityForm.on_model(Lane)):
    pass


class PoolReservationSearchForm(SingleClusterReservationSearchMixin, BaseReservationSearchForm):
    reservation_model = LaneReservation
