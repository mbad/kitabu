from django import forms
from django.forms import ValidationError
from django.db.models import Q

from kitabu.forms import KitabuForm


class BaseReservationSearchForm(KitabuForm):
    start = forms.DateTimeField()
    end = forms.DateTimeField()

    def clean(self):
        if 'start' in self.cleaned_data and 'end' in self.cleaned_data:
            start = self.cleaned_data['start']
            end = self.cleaned_data['end']
            if not end > start:
                raise ValidationError('Make sure end date is later than start date')
        return super(BaseReservationSearchForm, self).clean()

    def search(self, *args, **kwargs):
        start = self.cleaned_data['start']
        end = self.cleaned_data['end']

        return self.reservation_model.objects.filter(
            Q(start__gte=start, start__lt=end) | Q(end__gt=start, end__lte=end) | Q(start__lte=start, end__gte=end),
            *args, **kwargs
        )


class SingleSubjectReservationSearchMixin(object):
    '''
    This class should be mixed in before some descendant of
    BaseAvailabilityForm as it suplies search method which calls its super
    '''
    def search(self, subject, **kwargs):
        return super(SingleSubjectReservationSearchMixin, self).search(subject=subject, **kwargs)


class SingleClusterReservationSearchMixin(object):
    '''
    This class should be mixed in before some descendant of
    BaseAvailabilityForm as it suplies search method which calls its super
    '''
    def search(self, subject_model_manager, **kwargs):
        return super(SingleClusterReservationSearchMixin, self).search(subject__in=subject_model_manager.all(),
                                                                       **kwargs)
