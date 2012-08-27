from kitabu.reservation_forms import (
        BaseReservationForm, ReservationWithSizeForm)
from kitabu.availability_forms import ExclusiveAvailabilityForm

from models import LaneReservation, Lane


class LaneReservationForm(BaseReservationForm, ReservationWithSizeForm):
    reservation_model = LaneReservation


class AvailableLanesSearchForm(ExclusiveAvailabilityForm.on_model(Lane)):
    pass
