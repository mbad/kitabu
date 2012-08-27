from django import forms
from django.db.models import Q
from django.forms import ValidationError


class BaseAvailabilityForm(forms.Form):
    start = forms.SplitDateTimeField()
    end = forms.SplitDateTimeField()

    def clean(self):
        if 'start' in self.cleaned_data and 'end' in self.cleaned_data:
            start = self.cleaned_data['start']
            end = self.cleaned_data['end']
            if not end > start:
                raise ValidationError(
                        'Make sure end date is later than start date')
        return super(BaseAvailabilityForm, self).clean()

    @classmethod
    def on_model(cls, model):
        '''Give subject model and inherit. E.g.
        class YourSearchForm(SearchAvailableSubjectsForm.on_model(YourModel)):
            pass
        '''
        cls.subject_model = model
        cls.reservation_model = model.get_reservation_model()
        return cls


class ExclusiveAvailabilityForm(BaseAvailabilityForm):
    def search(self):
        start = self.cleaned_data['start']
        end = self.cleaned_data['end']
        colliding_reservations = self.reservation_model.objects.filter(
                Q(start__gte=start, start__lt=end)
                | Q(end__gt=start, end__lte=end))
        disqualified_subjects = colliding_reservations.values('subject')\
                .distinct()
        good_subjects = self.subject_model.objects.filter(
                ~Q(id__in=disqualified_subjects))
        return good_subjects
