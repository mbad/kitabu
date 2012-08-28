from kitabu.reservation_forms import (
        BaseReservationForm, ReservationWithSizeForm)

from kitabu.availability_forms import ExclusiveAvailabilityFormForOwnedSubject

from lanes.models import Lane


class AvailableLanesSearchForm(
        ExclusiveAvailabilityFormForOwnedSubject.on_model(Lane)):
    pass
