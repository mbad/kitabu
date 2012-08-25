from django import template
from lanes.models import Lane

register = template.Library()


@register.inclusion_tag('lanes_list.html')
def lanes_list():
    lanes = Lane.objects.all()
    return {'lanes': lanes}
