'''
Created on May 17, 2013

@author: hieunv
'''
from django.conf.urls import patterns, url
from apps.auth import views
urlpatterns = patterns('',
    url(r'^/signin/?$', views.sign_in, name='signin'),
    url(r'^/signout/?$', views.sign_out, name='signout'),
)