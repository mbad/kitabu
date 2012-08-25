from django import forms
from kitabu.reservation_forms import (
        BaseReservationForm, ReservationWithSizeForm)

from models import LaneReservation


class LaneReservationForm(BaseReservationForm, ReservationWithSizeForm):
    reservation_model = LaneReservation
