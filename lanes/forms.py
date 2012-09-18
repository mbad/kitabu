from kitabu.forms.reservation import ReservationWithSizeForm
from kitabu.forms.availability import ExclusiveAvailabilityForm
from kitabu.forms.validators import FullHourValidator, FullMinuteValidator

from models import LaneReservation, Lane


class LaneReservationForm(ReservationWithSizeForm):
    reservation_model = LaneReservation
    validators = {
                  'start': [FullHourValidator(message=u'Bad start time (full hours allowed)')],
                  'end': [FullMinuteValidator(message=u'Bad end time (full minutes allowed)')]}


class AvailableLanesSearchForm(ExclusiveAvailabilityForm.on_model(Lane)):
    pass
