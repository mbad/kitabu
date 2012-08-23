from django import forms


class LaneReservationForm(forms.Form):
    start = forms.SplitDateTimeField()
    end = forms.SplitDateTimeField()
    size = forms.IntegerField(min_value=1)