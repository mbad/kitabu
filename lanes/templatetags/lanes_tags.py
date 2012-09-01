from django import template
from lanes.models import Lane

register = template.Library()


@register.inclusion_tag('lanes_list.html')
def lanes_list(pool=None):
    if pool is None:
        lanes = Lane.objects.all()
    else:
        lanes = pool.lanes.all()

    return {'lanes': lanes}
