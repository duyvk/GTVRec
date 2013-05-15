'''
Created on May 13, 2013

@author: rega
'''
from django.conf.urls import patterns, url, include
import settings
urlpatterns = patterns('',
    url(r'^movie', include('apps.movies.urls', namespace='movies')),
)

if settings.DEBUG:
    urlpatterns += patterns('',
        (r'^media/(?P<path>.*)$', 'django.views.static.serve', { 'document_root': settings.MEDIA_ROOT }),
        (r'^static/(?P<path>.*)$', 'django.views.static.serve', { 'document_root': settings.STATIC_ROOT }),
    )