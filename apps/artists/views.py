'''
Created on May 24, 2013

@author: hieunv
'''
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from apps.movies.models import Artist
def index(request):
    return render_to_response("", {
    }, context_instance=RequestContext(request))
def movies(request, artist_id):
    if (artist_id):
        artist = Artist.objects.get(id=artist_id)
        if artist.artist_job == "DIRECTOR":
            movies = artist.movies_movie_directed.all()
        elif artist.artist_job == "CAST":
            movies = artist.movies_movie_acted.all()
        return render_to_response("artist/movie.html", {
            'artist' : artist,
            'movies' : movies,
        }, context_instance=RequestContext(request)) 
    else:
        artist = Artist.objects.get(id=1)
        if artist.artist_job == "DIRECTOR":
            movies = artist.movies_movie_directed.all()
        elif artist.artist_job == "CAST":
            movies = artist.movies_movie_acted.all()
        return render_to_response("artist/movie.html", {
            'artist' : artist,
            'movies' : movies,
        }, context_instance=RequestContext(request)) 