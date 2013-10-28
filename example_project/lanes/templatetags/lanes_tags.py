from django import template
from lanes.models import Lane

register = template.Library()


@register.inclusion_tag('lanes/list.html')
def lanes_list(pool=None):
    if pool is None:
        lanes = Lane.objects.all()
    else:
        lanes = pool.lanes.all()

    return {'lanes': lanes}


@register.simple_tag
def nice_period(period):
    def _format(datetime):
        return datetime.strftime('%d.%m.%Y %H:%M')

    formatted = [_format(period[0]), _format(period[1])]
    return ' - '.join(formatted)
