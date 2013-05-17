'''
Created on May 17, 2013

@author: hieunv
'''
from django.conf.urls import patterns, url
from apps.musics import views
urlpatterns = patterns('',
    url(r'^/?$', views.index, name='index'),
)