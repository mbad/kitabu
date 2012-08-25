#-*- coding=utf-8 -*-

from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404

from kitabu.exceptions import CapacityExceeded
from forms import LaneReservationForm
from models import Lane


def index(request):
    lanes = Lane.objects.all()
    return render(request, 'index.html', {'lanes': lanes})


#@login_required
def reserve(request, lane_id):
    lane = get_object_or_404(Lane, pk=lane_id)
    capacity_exceeded_msg = ''

    if request.POST:
        form = LaneReservationForm(request.POST)
        if form.is_valid():
            start = form.cleaned_data['start']
            end = form.cleaned_data['end']
            size = form.cleaned_data['size']

            try:
                lane.reserve(start, end, size, owner=request.user)
                return HttpResponseRedirect('reserve', lane_id)
            except CapacityExceeded:
                capacity_exceeded_msg = 'Capacity exceeded'
    else:
        form = LaneReservationForm()

    return render(
            request,
            'reserve.html',
            {
                'lane': lane,
                'form': form,
                'capacity_exceeded_msg': capacity_exceeded_msg
            })
