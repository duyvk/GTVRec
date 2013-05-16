'''
Created on May 14, 2013

@author: hieunv
'''
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from apps.movies.forms import MovieWeightsForm

def index(request):
    return render_to_response("movies/index.html", {
        'f' : range(20),
        'form' : MovieWeightsForm(),
    } ,context_instance=RequestContext(request))