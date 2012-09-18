from kitabu.reservation_forms import ReservationWithSizeForm
from kitabu.availability_forms import ExclusiveAvailabilityForm
from kitabu.form_validators import FullHourValidator, FullMinuteValidator

from models import LaneReservation, Lane


class LaneReservationForm(ReservationWithSizeForm):
    reservation_model = LaneReservation
    validators = {
                  'start': [FullHourValidator(message=u'Bad start time (full hours allowed)')],
                  'end': [FullMinuteValidator(message=u'Bad end time (full minutes allowed)')]}


class AvailableLanesSearchForm(ExclusiveAvailabilityForm.on_model(Lane)):
    pass
