#-*- coding=utf-8 -*-

from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required

from kitabu.search.available import ExclusivelyAvailableSubjects

from forms import LaneReservationForm, AvailableLanesSearchForm
from models import Lane


def index(request):
    lanes = Lane.objects.all()
    return render(request, 'lanes/index.html', {'lanes': lanes})


@login_required
def reserve(request, lane_id):
    lane = get_object_or_404(Lane, pk=lane_id)
    success_msg = ""

    if request.POST:
        form = LaneReservationForm(request.POST)
        if form.is_valid():
            reservation = form.make_reservation(owner=request.user, subject=lane)
            if reservation:
                form = LaneReservationForm()
                success_msg = "Reservation successful"
    else:
        form = LaneReservationForm()

    return render(
        request,
        'lanes/reserve.html',
        {
            'lane': lane,
            'pool': lane.cluster,
            'form': form,
            'success_msg': success_msg,
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
