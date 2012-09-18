#-*- coding=utf-8 -*-

from django.shortcuts import render, get_object_or_404
from models import Pool
from forms import AvailableLanesSearchForm, PoolReservationsSearchForm


def index(request):
    pools = Pool.objects.all()
    return render(request, 'pools_index.html', {'pools': pools})


def show(request, pool_id):
    pool = get_object_or_404(Pool, pk=pool_id)

    if 'reservations-start' in request.GET:
        reservations_form = PoolReservationsSearchForm(request.GET, prefix='reservations')
        form = AvailableLanesSearchForm(prefix='available_subjects')
    elif 'available_subjects-start' in request.GET:
        form = AvailableLanesSearchForm(request.GET, prefix='available_subjects')
        reservations_form = PoolReservationsSearchForm(prefix='reservations')
    else:
        reservations_form = PoolReservationsSearchForm(prefix='reservations')
        form = AvailableLanesSearchForm(prefix='available_subjects')

    results = form.search(cluster=pool) if form.is_valid() else []
    reservations = reservations_form.search(subject_model_manager=pool.subjects) if reservations_form.is_valid() else []

    return render(request, 'pools_show.html', {
                                               'reservations': reservations,
                                               'pool': pool,
                                               'form': form,
                                               'reservations_form': reservations_form,
                                               'results': results})
