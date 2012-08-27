#-*- coding=utf-8 -*-

from django.shortcuts import render, get_object_or_404

from forms import LaneReservationForm, AvailableLanesSearchForm
from models import Lane


def index(request):
    lanes = Lane.objects.all()
    return render(request, 'index.html', {'lanes': lanes})


#@login_required
def reserve(request, lane_id):
    lane = get_object_or_404(Lane, pk=lane_id)
    success_msg = ""

    if request.POST:
        form = LaneReservationForm(request.POST)
        if form.is_valid():
            reservation = form.make_reservation(owner=request.user,
                    subject=lane)
            if reservation:
                form = LaneReservationForm()
                success_msg = "Reservation successful"
    else:
        form = LaneReservationForm()

    return render(
            request,
            'reserve.html',
            {
                'lane': lane,
                'form': form,
                'success_msg': success_msg,
            })


def search(request):
    if request.GET:
        form = AvailableLanesSearchForm(request.GET)
    else:
        form = AvailableLanesSearchForm()
    results = form.search() if form.is_valid() else []

    return render(request, 'search.html', {'form': form, 'results': results})
