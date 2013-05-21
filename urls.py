'''
Created on May 13, 2013

@author: hieunv
'''
from django.conf.urls import patterns, url, include
import settings
from apps.home import views
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^/?$', views.index, name='home_index'),
    url(r'^home', include('apps.home.urls', namespace='home')),
    url(r'^movie', include('apps.movies.urls', namespace='movies')),
    url(r'^music', include('apps.musics.urls', namespace='musics')),
    url(r'^clip', include('apps.clips.urls', namespace='clips')),
    url(r'^auth', include('apps.auth.urls', namespace='auth')),
    url(r'^admin/', include(admin.site.urls)),
)

if settings.DEBUG:
    urlpatterns += patterns('',
        (r'^media/(?P<path>.*)$', 'django.views.static.serve', { 'document_root': settings.MEDIA_ROOT }),
      # (r'^static/(?P<path>.*)$', 'django.views.static.serve', { 'document_root': settings.STATIC_ROOT }),
    )
