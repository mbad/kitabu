#-*- coding=utf-8 -*-

import urllib

from django.shortcuts import render, get_object_or_404

from kitabu.search.available import Clusters as ClustersSearcher, Subjects as SubjectSearcher, FindPeriod
from kitabu.search.reservations import SingleSubjectManagerReservationSearch
from lanes.models import Lane, LaneReservation
from models import Pool
from forms import PoolReservationsSearchForm, ClusterSearchForm, PeriodSearchForm


cluster_searcher = ClustersSearcher(subject_model=Lane, cluster_model=Pool)


def index(request):
    form = ClusterSearchForm(request.GET or None)
    if form.is_valid():
        results = cluster_searcher.search(**form.cleaned_data)
        lane_search_query_string = urllib.urlencode({
            'start': form.cleaned_data['start'],
            'end': form.cleaned_data['end'],
            'required_size': 1})
    else:
        results = None
        lane_search_query_string = ''

    return render(
        request,
        'pools/index.html',
        {
            'form': form,
            'available_pools': results,
            'lane_search_query_string': lane_search_query_string,
        }
    )


def show(request, pool_id):
    pool = get_object_or_404(Pool, pk=pool_id)

    return render(request, 'pools/show.html', {'pool': pool})


def availability(request, pool_id):
    pool = get_object_or_404(Pool, pk=pool_id)

    form = ClusterSearchForm(request.GET or None)

    searcher = SubjectSearcher(Lane, pool.lanes)

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

    reservations = (
        searcher.search(**form.cleaned_data)
        if form.is_valid() else
        LaneReservation.objects.filter(subject__cluster=pool)
        if not request.GET else
        []
    )

    return render(
        request,
        'pools/reservations.html',
        {
            'reservations': reservations,
            'pool': pool,
            'form': form,
        }
    )


def available_periods(request, pool_id):
    pool = get_object_or_404(Pool, pk=pool_id)

    form = PeriodSearchForm(request.GET) if request.GET else PeriodSearchForm()

    lanes_and_periods = [
        (subject, FindPeriod().search(subject=subject, **form.cleaned_data))
        for subject in pool.subjects.all()] if form.is_valid() else []

    return render(
        request,
        'pools/periods.html',
        {
            'lanes_and_periods': lanes_and_periods,
            'pool': pool,
            'form': form,
        }
    )
