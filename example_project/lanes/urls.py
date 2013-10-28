from django.conf.urls import patterns, url


urlpatterns = patterns(
    '',
    url(r'^reserve/(?P<lane_id>\d+)/$', 'lanes.views.reserve',
        name='reserve-lane'),
    url(r'^search$', 'lanes.views.search', name='search-free-lanes'),
)
