from collections import defaultdict
from django import forms
from django.db.models import Q
from django.forms import ValidationError


class BaseAvailabilityForm(forms.Form):
    start = forms.SplitDateTimeField()
    end = forms.SplitDateTimeField()

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
    def search(self):
        '''
        Search for available subjects in a time period
        '''
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
    size = forms.IntegerField(required=False)

    def search(self):

        start = self.cleaned_data['start']
        end = self.cleaned_data['end']
        needed_size = self.cleaned_data.get('size', 1)

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
                timelines[res.subject][res.end] -= res.size

        disqualified_subjects = []
        for subject, timeline in timelines.iteritems():
            reservations_cnt = 0
            max_reservations = 0
            for moment in sorted(timeline.keys()):
                reservations_cnt += timeline[moment]
                if reservations_cnt > max_reservations:
                    max_reservations = reservations_cnt
                    if reservations_cnt + needed_size > subject.size:
                        disqualified_subjects.append(subject.id)
                        break
        return self.subject_model_manager.filter(~Q(id__in=disqualified_subjects), size__gte=needed_size)
