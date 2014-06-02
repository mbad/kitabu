from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
from django.conf import settings
admin.autodiscover()

urlpatterns = patterns(
    '',
    url(r'^$', 'pools.views.index'),

    url(r'^admin/', include(admin.site.urls)),

    url(r'^lanes/', include('lanes.urls')),
    url(r'^pools/', include('pools.urls')),

    (r'^accounts/', include('registration.backends.simple.urls')),
)
