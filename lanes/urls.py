from django.conf.urls import patterns, include, url


urlpatterns = patterns('',
    url(r'^$', 'lanes.views.index'),
    url(r'^reserve/(?P<lane_id>\d+)/$', 'lanes.views.reserve'),
)