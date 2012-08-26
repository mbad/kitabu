from django import forms


class SearchAvailableSubjectsForm(forms.Form):
    start = forms.DateTimeField()
    end = forms.DateTimeField()
