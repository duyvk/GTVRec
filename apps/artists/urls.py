'''
Created on May 24, 2013

@author: hieunv
'''
from django.conf.urls import patterns, url
from apps.artists import views
urlpatterns = patterns('',
    url(r'^/?$', views.index, name='index'),
    url(r'^/movie/(?P<artist_id>\d+)/?$', views.movies, name='movie'),
)