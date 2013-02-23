#-*- coding=utf-8 -*-

from django.shortcuts import render, get_object_or_404

from kitabu.search.available import ClusterFiniteAvailability, FiniteAvailability
from kitabu.search.reservations import SingleSubjectManagerReservationSearch
from lanes.models import Lane, LaneReservation
from models import Pool
from forms import PoolReservationsSearchForm, ClusterSearchForm


cluster_searcher = ClusterFiniteAvailability(subject_model=Lane,
                                             cluster_model=Pool,
                                             )


def index(request):
    form = ClusterSearchForm(request.GET or None)
    if form.is_valid():
        results = cluster_searcher.search(**form.cleaned_data)
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

    form = ClusterSearchForm(request.GET or None)

    searcher = FiniteAvailability(Lane, pool.subjects)

    available_lanes = searcher.search(**form.cleaned_data) if form.is_valid() else []

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

    searcher = SingleSubjectManagerReservationSearch(
        reservation_model=LaneReservation, subject_manager=pool.subjects)

    reservations = searcher.search(**form.cleaned_data) if form.is_valid() else []

    return render(
        request,
        'pools/reservations.html',
        {
            'reservations': reservations,
            'pool': pool,
            'form': form,
        }
    )