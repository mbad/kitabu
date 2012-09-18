from kitabu.forms.availability import FiniteAvailabilityForm, OneClusterAvailabilityFormMixin
from kitabu.forms.reservation_search import SingleClusterReservationSearchMixin, BaseReservationSearchForm

from lanes.models import Lane, LaneReservation


class AvailableLanesSearchForm(
        OneClusterAvailabilityFormMixin,
        FiniteAvailabilityForm.on_model(Lane)):
    pass


class PoolReservationsSearchForm(SingleClusterReservationSearchMixin, BaseReservationSearchForm):
    reservation_model = LaneReservation
