'''
Created on May 14, 2013

@author: hieunv
'''
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from apps.movies.forms import MovieWeightsForm
from apps.movies.models import *
def index(request):
    
    return render_to_response("movies/index.html", {
        'movies' : Movie.objects.all(),
        'form' : MovieWeightsForm(),
    } ,context_instance=RequestContext(request))
def view(request, page):
    return render_to_response("movies/view.html", {}, context_instance=RequestContext());