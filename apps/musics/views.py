'''
Created on May 17, 2013

@author: hieunv
'''
from django.shortcuts import render_to_response
from django.template.context import RequestContext
def index(request):
    return render_to_response('musics/index.html', {
    }, context_instance=RequestContext(request));