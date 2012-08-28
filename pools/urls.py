from django.conf.urls import patterns, url


urlpatterns = patterns('',
    url(r'^$', 'pools.views.index', name='list-pools'),
    url(r'^(?P<pool_id>\d+)/$', 'pools.views.show',
        name='show-pool'),
)
