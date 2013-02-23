#-*- coding=utf-8 -*-

from django import template
from pools.models import Pool

register = template.Library()


@register.inclusion_tag('pools/list.html')
def pools_list():
    pools = Pool.objects.all()
    return {'pools': pools}
