'''
Created on May 14, 2013

@author: hieunv
'''
from django.shortcuts import render_to_response
from django.template.context import RequestContext

def index(request):
    data = { }
    data['f'] =  range(100)
    return render_to_response("movies/index.html", data ,context_instance=RequestContext(request))