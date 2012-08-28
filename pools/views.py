#-*- coding=utf-8 -*-

from django.shortcuts import render, get_object_or_404
from models import Pool
from forms import AvailableLanesSearchForm


def index(request):
    pools = Pool.objects.all()
    return render(request, 'pools_index.html', {'pools': pools})


def show(request, pool_id):
    pool = get_object_or_404(Pool, pk=pool_id)

    if request.GET:
        form = AvailableLanesSearchForm(request.GET)
    else:
        form = AvailableLanesSearchForm()
    results = form.search(groupping_object=pool) if form.is_valid() else []

    return render(request, 'pools_show.html', {'pool': pool, 'form': form,
            'results': results})
