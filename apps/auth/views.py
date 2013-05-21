'''
Created on May 17, 2013

@author: hieunv
'''
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.http.response import HttpResponseRedirect
from django.contrib.auth import login
from django.contrib.auth import authenticate
from django.contrib.auth.views import logout_then_login
def sign_in(request):
    if request.user.is_authenticated():
        return HttpResponseRedirect('/home/index')
    if request.method == 'GET':
        return sign_in_get(request)
    elif request.method == 'POST':
        return sign_in_post(request)
    
def sign_in_get(request):
    return render_to_response('auth/sign_in.html', {
              
    }, context_instance=RequestContext(request))
def sign_in_post(request):
    uname = request.POST['uname']
    upass = request.POST['upass']
    if not request.POST.get('remember_me', None):
        request.session.set_expiry(0)
    u = authenticate(username=uname, password=upass)
    if u is not None:
        if u.is_active:
            login(request, u)
            return HttpResponseRedirect('/home/index')
        else:
            return HttpResponseRedirect('/auth/signin')
    else:
        return HttpResponseRedirect('/auth/signin');
def sign_out(request):
    return logout_then_login(request, '/home/index');