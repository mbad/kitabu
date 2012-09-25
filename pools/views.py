#-*- coding=utf-8 -*-

from django.shortcuts import render, get_object_or_404
from models import Pool
from forms import AvailableLanesSearchForm, PoolReservationsSearchForm, ClusterSearchForm


def index(request):
    Form = ClusterSearchForm
    form = Form(request.GET) if request.GET else Form()
    if form.is_valid():
        results = form.search()
    else:
        results = None
    return render(
        request,
        'pools/index.html',
        {
            'form': form,
            'available_pools': results,
        }
    )


def show(request, pool_id):
    pool = get_object_or_404(Pool, pk=pool_id)

    return render(request, 'pools/show.html', {'pool': pool})


def availability(request, pool_id):
    pool = get_object_or_404(Pool, pk=pool_id)

    Form = AvailableLanesSearchForm

    form = Form(request.GET) if request.GET else Form()

    available_lanes = form.search(cluster=pool) if form.is_valid() else []

    return render(
        request,
        'pools/availability.html',
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
        'pools/reservations.html',
        {
            'reservations': reservations,
            'pool': pool,
            'form': form,
        }
    )
