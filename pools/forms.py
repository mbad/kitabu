from kitabu.availability_forms import FiniteAvailabilityForm, OneClusterAvailabilityFormMixin

from lanes.models import Lane


class AvailableLanesSearchForm(
        OneClusterAvailabilityFormMixin,
        FiniteAvailabilityForm.on_model(Lane)):
    pass
