'''
Created on May 16, 2013

@author: hieunv
'''
from django.conf.urls import patterns, url
from apps.home import views
urlpatterns = patterns('',
    url(r'^/?$', views.index, name='index'),
    url(r'^/index/?$', views.index, name='index'),
)
