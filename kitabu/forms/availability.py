from collections import defaultdict
from datetime import timedelta

from django import forms
from django.db.models import Q
from django.forms import ValidationError

from kitabu.forms import KitabuSearchForm
from kitabu.utils import Timeline


class BaseAvailabilityForm(KitabuSearchForm):
    start = forms.DateTimeField(widget=forms.DateTimeInput(attrs={'class': 'kitabu-datetime-field'}))
    end = forms.DateTimeField(widget=forms.DateTimeInput(attrs={'class': 'kitabu-datetime-field'}))

    def _get_subject_model_manager(self):
        if not hasattr(self, '_subject_model_manager'):
            self._subject_model_manager = self.subject_model.objects
        return self._subject_model_manager

    def _set_subject_model_manager(self, value):
        self._subject_model_manager = value

    subject_model_manager = property(_get_subject_model_manager, _set_subject_model_manager)

    def clean(self):
        if 'start' in self.cleaned_data and 'end' in self.cleaned_data:
            start = self.cleaned_data['start']
            end = self.cleaned_data['end']
            if not end > start:
                raise ValidationError('Make sure end date is later than start date')
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


class OneClusterAvailabilityFormMixin(object):
    '''
    This class should be mixed in before some descendant of
    BaseAvailabilityForm as it suplies search method which calls its super
    '''
    def search(self, cluster, **kwargs):
        self.subject_model_manager = cluster.subjects.all()
        return super(OneClusterAvailabilityFormMixin, self).search(**kwargs)


class ExclusiveAvailabilityForm(BaseAvailabilityForm):
    '''
    Form for searching subjects available in certain time period.
    Exclusive means only one reservation at a time is possible.
    '''

    def search(self):
        start = self.cleaned_data['start']
        end = self.cleaned_data['end']
        colliding_reservations = self.reservation_model.objects.filter(
            Q(start__gte=start, start__lt=end) | Q(end__gt=start, end__lte=end),
            subject__in=self.subject_model_manager.all()
        )
        disqualified_subjects = colliding_reservations.values('subject') .distinct()
        good_subjects = self.subject_model_manager.filter(~Q(id__in=disqualified_subjects))
        return good_subjects


class FiniteAvailabilityForm(BaseAvailabilityForm):
    '''
    Form for searching subjects available in certain time period.
    Finite availablity means only certain number of reservations at a time is possible.
    '''
    size = forms.IntegerField(initial=1)

    def search(self):

        start = self.cleaned_data['start']
        end = self.cleaned_data['end']
        required_size = self.cleaned_data.get('size')

        colliding_reservations = self.reservation_model.objects.filter(
            (
                Q(start__gte=start, start__lt=end)   # start in scope
                | Q(end__gt=start, end__lte=end)     # end in scope
                | Q(start__lte=start, end__gte=end)  # covers whole scope
            ),
            subject__in=self.subject_model_manager.all(),
        ).select_related('subject')

        timelines = defaultdict(lambda: defaultdict(lambda: 0))

        for res in colliding_reservations:
            res_start = start if res.start < start else res.start
            timelines[res.subject][res_start] += res.size
            if res.end < end:
                timelines[res.end] -= res.size

        disqualified_subjects = []
        for subject, timeline in timelines.iteritems():
            reservations_cnt = 0
            max_reservations = 0
            for moment in sorted(timeline.keys()):
                reservations_cnt += timeline[moment]
                if reservations_cnt > max_reservations:
                    max_reservations = reservations_cnt
                    if reservations_cnt + required_size > subject.size:
                        disqualified_subjects.append(subject.id)
                        break
        return self.subject_model_manager.filter(~Q(id__in=disqualified_subjects), size__gte=required_size)


class VaryingDateAvailabilityForm(BaseAvailabilityForm):
    duration = forms.IntegerField(min_value=1)

    def get_duration(self):
        '''
        This method is supposed to somehow figure out for how long reservation needs to be done.
        Must return datetime.timedelta.
        This default implementation gets integer named 'duration' from cleaned_data and treats it as
        duration in days
        '''
        return timedelta(self.cleaned_data['duration'])

    def get_size(self):
        '''
        This method is supposed to somehow figure out how big reservation needs to be.
        Must return integer.

        This very simple implementation is suitable for Exclusive subjects and reservations
        '''
        return 1

    def get_subject(self):
        '''
        This method must return subject on which the search is about to be performed

        It only needs to be implemented if search method is to be used without providing
        subject, e.g. when subject is to be retrieved basing on cleaned_data like subject_id
        '''
        raise NotImplementedError

    def search(self, subject=None):
        if not subject:
            subject = self.get_subject()

        start = self.cleaned_data['start']
        end = self.cleaned_data['end']
        required_duration = self.get_duration()
        required_size = self.get_size()

        timeline = Timeline(subject, start, end)

        available_size = timeline.subject.size
        available_dates = []
        potential_start = timeline.start
        current_date = timeline.end
        current_size = 0

        for current_date, delta in timeline:
            current_size += delta
            if current_size + required_size <= available_size:
                if potential_start is None:
                    potential_start = current_date
            elif potential_start:
                if current_date - potential_start >= required_duration:
                    available_dates.append((potential_start, current_date))
                potential_start = None
        if (
            potential_start is not None
            and current_size + required_size <= available_size
            and end - potential_start >= required_duration
        ):
            available_dates.append((potential_start, end))
        return available_dates


class VaryingDateAndSizeAvailabilityForm(VaryingDateAvailabilityForm):
    size = forms.IntegerField(min_value=1)

    def get_size(self):
        return self.cleaned_data['size']
