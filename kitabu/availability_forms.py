from collections import defaultdict
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


#class OneClusterAvailabilityForm(BaseAvailabilityForm):
#    def search(self, cluster, **kwargs):


class ExclusiveAvailabilityForm(BaseAvailabilityForm):
    def search(self, reservations_filter_builder=lambda q: q,
               subject_model_manager=None):
        '''
        Search for available subjects in a time period

        Additional params:
            reservations_filter_builder : function(Q_object) -> Q_object
                Modifier for the default colliding_reservations search
                conditions.

            subject_model_manager : Subject.objects
                Objects manager for Subject class
        '''
        if (subject_model_manager == None):
            subject_model_manager = self.subject_model.objects

        start = self.cleaned_data['start']
        end = self.cleaned_data['end']
        colliding_reservations = self.reservation_model.objects.filter(
                reservations_filter_builder(
                    Q(start__gte=start, start__lt=end)
                    | Q(end__gt=start, end__lte=end)))
        disqualified_subjects = colliding_reservations.values('subject')\
                .distinct()
        good_subjects = subject_model_manager.filter(
                ~Q(id__in=disqualified_subjects))
        return good_subjects


class FiniteAvailabilityForm(BaseAvailabilityForm):
    def search(
            self,
            needed_size=1,
            reservations_filter_builder=lambda q: q,
            subject_model_manager=None):
        if (subject_model_manager is None):
            subject_model_manager = self.subject_model.objects

        start = self.cleaned_data['start']
        end = self.cleaned_data['end']
        colliding_reservations = self.reservation_model.objects.filter(
            reservations_filter_builder(
                Q(start__gte=start, start__lt=end)   # start in scope
                | Q(end__gt=start, end__lte=end)     # end in scope
                | Q(start__lte=start, end__gte=end)  # covers whole scope
            )).select_related('subject')

        timelines = defaultdict(lambda x: defaultdict(lambda x: 0))

        for res in colliding_reservations:
            res_start = start if res.start < start else res.start
            timelines[res.subject][res_start] += res.size
            if res.end < end:
                timelines[res.end] -= res.size

        good_subjects = {}
        for subject, timeline in timelines.iteritems():
            reservations_cnt = 0
            max_reservations = 0
            for moment in sorted(timeline.keys()):
                reservations_cnt += timelines[moment]
                if reservations_cnt > max_reservations:
                    max_reservations = reservations_cnt
                    if reservations_cnt + needed_size > subject.size:
                        break
            available_size = subject.size = max_reservations
            if available_size >= needed_size:
                good_subjects[subject] = available_size
        return good_subjects





class ExclusiveAvailabilityFormForOwnedSubject(ExclusiveAvailabilityForm):
    def search(self, cluster):
        '''
        Search for available cluster subjects in a time period
        '''
        filter_builder = lambda q:\
            Q(subject__cluster_id=cluster.id) & q

        return super(ExclusiveAvailabilityFormForOwnedSubject, self).\
            search(reservations_filter_builder=filter_builder,
                subject_model_manager=cluster.subjects)
