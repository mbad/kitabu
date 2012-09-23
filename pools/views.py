#-*- coding=utf-8 -*-

from django.shortcuts import render, get_object_or_404
from models import Pool
from forms import AvailableLanesSearchForm, PoolReservationsSearchForm


def index(request):
    pools = Pool.objects.all()
    return render(request, 'pools_index.html', {'pools': pools})


def show(request, pool_id):
    pool = get_object_or_404(Pool, pk=pool_id)

    return render(request, 'pools_show.html', {'pool': pool})


def availability(request, pool_id):
    pool = get_object_or_404(Pool, pk=pool_id)

    Form = AvailableLanesSearchForm

    form = Form(request.GET) if request.GET else Form()

    available_lanes = form.search(cluster=pool) if form.is_valid() else []

    return render(
        request,
        'pools_availability.html',
        {
            'pool': pool,
            'form': form,
            'available_lanes': available_lanes
        }
    )


def reservations(request, pool_id):
    pool = get_object_or_404(Pool, pk=pool_id)

    Form = PoolReservationsSearchForm

    form = Form(request.GET) if request.GET else Form()

    reservations = form.search(subject_model_manager=pool.subjects) if form.is_valid() else []

    return render(
        request,
        'pools_reservations.html',
        {
            'reservations': reservations,
            'pool': pool,
            'form': form,
        }
    )
