#-*- coding=utf-8 -*-

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.forms.util import ErrorList
from django.forms.formsets import formset_factory

from kitabu.search.available import ExclusivelyAvailableSubjects
from kitabu.exceptions import (
    ReservationError,
    InvalidPeriod,
    OverlappingReservations,
    SizeExceeded,
    TooManyReservations,
)

from spa.forms import RequiredFormSet
from spa.settings import MAX_LANE_RESERVATIONS_NR

from forms import LaneReservationForm, AvailableLanesSearchForm, LaneReservationsNrForm
from models import Lane, LaneReservationGroup


@login_required
def reserve(request, lane_id):
    try:
        forms_nr = int(request.GET.get('forms_nr', 1))
    except ValueError:
        forms_nr = 1

    lane_reservations_nr_form = LaneReservationsNrForm({'forms_nr': forms_nr})

    forms_nr = max(1, forms_nr)

    lane = get_object_or_404(Lane, pk=lane_id)
    success_msg = ""

    ReservationFormset = formset_factory(LaneReservationForm, extra=forms_nr, max_num=MAX_LANE_RESERVATIONS_NR,
                                         formset=RequiredFormSet)

    if request.POST:
        formset = ReservationFormset(request.POST)

        if formset.is_valid():
            arguments = []
            for form in formset:
                arguments.append((lane, form.cleaned_data))
            try:
                LaneReservationGroup.reserve(*arguments, owner=request.user)
            except ReservationError as e:
                message = (
                    "Size exceeded. There aren't %s places available." % e.requested_size
                    if isinstance(e, SizeExceeded) else
                    "There are other reservations that overlap with selected period."
                    if isinstance(e, OverlappingReservations) else
                    e.message
                    if isinstance(e, InvalidPeriod) else
                    "You have reached limit of reservation for you account."
                    if isinstance(e, TooManyReservations) else
                    "Disallowed reservation parameters (%s)." % e.message
                )
                if "__all__" not in form._errors:
                    form._errors["__all__"] = ErrorList()
                form.errors['__all__'].append(message)
            else:
                return redirect('reserve-lane', lane_id)
    else:
        formset = ReservationFormset()

    return render(
        request,
        'lanes/reserve.html',
        {
            'lane': lane,
            'pool': lane.cluster,
            'formset': formset,
            'success_msg': success_msg,
            'lane_reservations_nr_form': lane_reservations_nr_form
        }
    )


available_lane_searcher = ExclusivelyAvailableSubjects(Lane)


def search(request):
    form = AvailableLanesSearchForm(request.GET or None)
    results = (
        available_lane_searcher.search(**form.cleaned_data)
        if form.is_valid()
        else []
    )

    return render(request, 'lanes/search.html', {'form': form, 'results': results})
