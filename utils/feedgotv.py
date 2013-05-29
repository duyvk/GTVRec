#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Created on Mar 13, 2013

@author: rega
'''
import time, sys
from Queue import Queue
from threading import Thread
from datetime import datetime
from django.db.models import Max
from movies.models import Movie, MovieVector, MovieVectorBoost, MovieVector2
from movieclips.models import MovieClip, MovieClipVector, MovieClipVectorBoost, MovieClipVector2
from clips.models import Clip, ClipVector, ClipVectorBoost, ClipVector2
from commons.models import RegionID, GenreID, Manufacturer, People, Tag, TopicID
from candidates.models import MovieCandidates, MovieClipCandidates, ClipCandidates
from django.db.utils import DatabaseError, IntegrityError
from filter import filter
from goTV_Recommender import settings
import mongoengine as mongo
from mongoengine import Q

#VIDEO_TYPE_LIST = [i[0] for i in VIDEO_TYPE]
# Capability tối đa của queue
BULK_INSERT_ITEMS = 100000
MOVIES_QUEUE = Queue(maxsize=BULK_INSERT_ITEMS)
MV_QUEUE = Queue(maxsize=BULK_INSERT_ITEMS)
CLIPS_QUEUE = Queue(maxsize=BULK_INSERT_ITEMS)

###################
# UTILITIES FUNCS #
###################
def create_region(regionId, regionName, mediaType):
    region = RegionID.objects.filter(regionID=regionId, media=mediaType)
    if not region:
        region = RegionID.objects.create(regionID=regionId,region_name=regionName,media=mediaType)
        return region
    return region[0]

def create_genre(genreId, genreName, mediaType):
    genre = GenreID.objects.filter(genreID=genreId, media=mediaType)
    if not genre:
        genre = GenreID.objects.create(genreID=genreId,genre_name=genreName, media=mediaType)
        return genre
    return genre[0]

def create_manufacturer(manufacturerName, mediaType):
    manufac = Manufacturer.objects.filter(manufacturer=manufacturerName, media=mediaType)
    if not manufac:
        manufac = Manufacturer.objects.create(manufacturer=manufacturerName, media=mediaType)
        return manufac
    return manufac[0]

def create_people(personId, personName, hisJob, mediaType):
#    if mediaType == 'movie':
#        people = People.objects.filter(person_name=personName,job=hisJob,media=mediaType)
#    elif mediaType == 'mv':
#        people = People.objects.filter(personID=personId,job=hisJob,media=mediaType)
#    else:
#        return None
    people = People.objects.filter(person_name=personName,job=hisJob,media=mediaType)
    if not people:
        people = People.objects.create(personID=personId,person_name=personName,job=hisJob,media=mediaType)
        return people
    return people[0]

def create_tag(the_tag, mediaType):
    tag = Tag.objects.filter(tags=the_tag, media=mediaType)
    if not tag:
        tag = Tag.objects.create(tags=the_tag, media=mediaType)
        return tag
    return tag[0]

def create_topic(topicId, topicName):
    topic = TopicID.objects.filter(topicID=topicId)
    if not topic:
        topic = TopicID.objects.create(topicID=topicId,topic_name=topicName)
        return topic
    return topic[0]

####################

class MovieInfo():
    def __init__(self, movieId, subcates, manufacturers, directors, casts, size, location, release_year,
                 tags, isHD, isPayment, isSingle, isDrama, isCinema, view_count, imdb=None, moreinfo = {}):
        """
        @param movieId: int
        @param subcates: list of int
        @param manufacturers: list of str
        @param directors: list of str
        @param casts: list of str
        @param size: int, second unit
        @param location: int
        @param release_year: int
        @param tags: list of str
        @param isHD: boolean
        @param isPayment: boolean
        @param isSingle: boolean
        @param isDrama: boolean
        @param isCinema: boolean
        @param view_count: int
        @param imdb: float
        """
        self.movieId = movieId
        self.subcates = subcates
        self.manufacturers = manufacturers
        self.directors = directors
        self.casts = casts
        self.size = size
        self.location = location
        self.release_year = release_year
        self.tags = tags
        self.isHD = isHD
        self.isPayment = isPayment
        self.isSingle = isSingle
        self.isDrama = isDrama
        self.isCinema = isCinema
        self.view_count = view_count
        # addition infos
        self.movie_name = moreinfo.get('movie_name', '')
        self.subcates_name = moreinfo.get('subcates_name', None)
        self.location_name = moreinfo.get('location_name', '')
        self.image_url = moreinfo.get('image_url', '')
        self.imdb = imdb
            
    def to_movie_model(self):
        mm = Movie(movieID=self.movieId)
        # update foreign key
        location = None
        if self.location:
            location = create_region(self.location, self.location_name, 'movie')
        # update m2m
        genres = []
        if self.subcates:
            for i in range(len(self.subcates)):
                subcate = self.subcates[i]
                subcate_name = ''
                if self.subcates_name:
                    try:
                        subcate_name = self.subcates_name[i]
                    except:
                        subcate_name = ''
                genre = create_genre(subcate, subcate_name, 'movie')
                genres.append(genre)
            #mm.subcategory.add(genres)
        
        manufacs = []
        if self.manufacturers:
            for i in range(len(self.manufacturers)):
                manufacturerName = self.manufacturers[i]
                manufac = create_manufacturer(manufacturerName, 'movie')
                manufacs.append(manufac)
            #mm.manufacturers.add(manufacs)
        
        coworkers = []
        if self.directors:
            for i in range(len(self.directors)):
                personName = self.directors[i]
                person = create_people(None, personName, 'director', 'movie')
                coworkers.append(person)
            #mm.directors.add(coworkers)
        
        casts = []
        if self.casts:
            for i in range(len(self.casts)):
                cast = self.casts[i]
                person = create_people(None, cast, 'cast', 'movie')
                casts.append(person)
            #mm.casts.add(casts)
        
        tags = []
        if self.tags:
            for i in range(len(self.tags)):
                the_tag = self.tags[i]
                tag = create_tag(the_tag, 'movie')
                tags.append(tag)
            #mm.tags.add(tags)
        
        # update fields
        mm.movie_name = self.movie_name
        if self.isSingle is not None:
            mm.is_single_movie = self.isSingle
        if self.imdb is not None:
            mm.IMDB_score = self.imdb
        if self.size is not None:
            mm.size = self.size
        if self.isHD is not None:
            mm.is_HD = self.isHD
        if self.release_year is not None:
            mm.release_year = self.release_year
        if self.isPayment:
            mm.payment = self.isPayment
        if self.isDrama:
            mm.movie_type = 'drama'
        elif self.isCinema:
            mm.movie_type = 'cinema'
        else:
            mm.movie_type = None
        mm.image_url = self.image_url
        if self.view_count is not None:
            mm.view_count = self.view_count
        
        return (mm, {
                     'location':location,
                    },
                    {'genres': genres, 
                     'manufacs': manufacs, 
                     'coworkers': coworkers, 
                     'casts': casts, 
                     'tags': tags,
                     })

class MovieClipInfo():
    def __init__(self, mvId, tags, publisher, release_year, artist, genres, topic, region, author,
                 play, download, comment, like, duration, subtitle, moreinfo = {}):
        """
        @param mvId: int
        @param tags: list of str
        @param publisher: str
        @param release_year: int
        @param artist: int
        @param genres: list of int
        @param topic: int
        @param region: int
        @param author: int
        @param play: int
        @param download: int
        @param comment: int
        @param like: int
        @param duration: int, second unit
        @param subtitle: boolean
        @param video_type: int
        """
        self.mvId = mvId
        self.tags = tags
        self.publisher = publisher
        self.release_year = release_year
        self.artist = artist
        self.genres = genres
        self.topic = topic
        self.region = region
        self.author = author
        self.play = play
        self.download = download
        self.comment = comment
        self.like = like
        self.duration = duration
        self.subtitle = subtitle
        #self.video_type = video_type
        # addtion infos
        self.mv_name = moreinfo.get('mv_name', '')
        self.lyric = moreinfo.get('lyric', False)
        self.dislike = moreinfo.get('dislike', 0)
        self.artist_name = moreinfo.get('artist_name', '')
        self.genres_name = moreinfo.get('genres_name', None)
        self.topic_name = moreinfo.get('topic_name', '')
        self.region_name = moreinfo.get('region_name','')
        self.author_name = moreinfo.get('author_name', '')
        self.image_url = moreinfo.get('image_url', '')
        
    def to_movieclip_model(self):
        mv = MovieClip(mvID=self.mvId)
        # update foreign key
        publisher = None
        if self.publisher:
            publisher = create_manufacturer(self.publisher, 'mv')
        
        artist = None    
        if self.artist or self.artist_name:
            artist = create_people(self.artist, self.artist_name, 'singer', 'mv')
        
        topic = None    
        if self.topic:
            topic = create_topic(self.topic, self.topic_name)
        
        region = None    
        if self.region:
            region = create_region(self.region, self.region_name, 'mv')
        
        author = None    
        if self.author or self.author_name:
            author = create_people(self.author, self.author_name, 'writer', 'mv')
        
        # update m2m
        tags = []
        if self.tags:
            for i in range(len(self.tags)):
                the_tag = self.tags[i]
                tag = create_tag(the_tag, 'mv')
                tags.append(tag)
            #mv.tags.add(tags)
            
        genres = []
        if self.genres:
            for i in range(len(self.genres)):
                genreid = self.genres[i]
                genre_name = ''
                if self.genres_name:
                    try:
                        genre_name = self.genres_name[i]
                    except:
                        genre_name = ''
                genre = create_genre(genreid, genre_name, 'mv')
                genres.append(genre)
            #mv.genre.add(genres)
        
        # update fields
        mv.mv_name = self.mv_name
        mv.lyric = self.lyric
        mv.release_year = self.release_year
        if self.play:
            mv.play_count = self.play
        if self.download:
            mv.download_count = self.download
        if self.comment:
            mv.comment_count = self.comment
        if self.like:
            mv.like_count = self.like
        if self.dislike:
            mv.dislike_count = self.dislike
        if self.duration:
            mv.duration = self.duration
        if self.subtitle:
            mv.subtitle = self.subtitle
        mv.image_url = self.image_url
#        if self.video_type in VIDEO_TYPE_LIST:
#            mv.video_type = self.video_type
#        else:
#            raise RuntimeError('video_type(%d) must be either MusicVideo(%d) or Clips(%d)') % \
#                        (self.video_type, VIDEO_TYPE_LIST[0], VIDEO_TYPE_LIST[1])
            
        return (mv,{
                    'publisher': publisher,
                    'artist':artist,
                    'topic':topic,
                    'region':region,
                    'author':author,
                    },
                   {
                    'tags':tags,
                    'genres':genres,
                    })


class ClipInfo():
    def __init__(self, clipId, tags, publisher, release_year, genres, region,
                 play, download, comment, like, duration, subtitle, moreinfo = {}):
        """
        @param clipId: int
        @param tags: list of str
        @param publisher: str
        @param release_year: int
        @param genres: list of int
        @param region: int
        @param play: int
        @param download: int
        @param comment: int
        @param like: int
        @param duration: int, second unit
        @param subtitle: boolean
        """
        self.clipId = clipId
        self.tags = tags
        self.publisher = publisher
        self.release_year = release_year
        self.genres = genres
        self.region = region
        self.play = play
        self.download = download
        self.comment = comment
        self.like = like
        self.duration = duration
        self.subtitle = subtitle
        # addtion infos
        self.clip_name = moreinfo.get('clip_name', '')
        self.dislike = moreinfo.get('dislike', 0)
        self.genres_name = moreinfo.get('genres_name', None)
        self.region_name = moreinfo.get('region_name','')
        self.image_url = moreinfo.get('image_url', '')
        
    def to_clip_model(self):
        clip = Clip(clipID=self.clipId)
        # update foreign key
        publisher = None
        if self.publisher:
            publisher = create_manufacturer(self.publisher, 'clip')
        
        region = None    
        if self.region:
            region = create_region(self.region, self.region_name, 'clip')
        
        # update m2m
        tags = []
        if self.tags:
            for i in range(len(self.tags)):
                the_tag = self.tags[i]
                tag = create_tag(the_tag, 'clip')
                tags.append(tag)
            
        genres = []
        if self.genres:
            for i in range(len(self.genres)):
                genreid = self.genres[i]
                genre_name = ''
                if self.genres_name:
                    try:
                        genre_name = self.genres_name[i]
                    except:
                        genre_name = ''
                genre = create_genre(genreid, genre_name, 'clip')
                genres.append(genre)
        
        # update fields
        clip.clip_name = self.clip_name
        clip.release_year = self.release_year
        if self.play:
            clip.play_count = self.play
        if self.download:
            clip.download_count = self.download
        if self.comment:
            clip.comment_count = self.comment
        if self.like:
            clip.like_count = self.like
        if self.dislike:
            clip.dislike_count = self.dislike
        if self.duration:
            clip.duration = self.duration
        if self.subtitle:
            clip.subtitle = self.subtitle
        clip.image_url = self.image_url
            
        return (clip,{
                    'publisher': publisher,
                    'region':region,
                    },
                   {
                    'tags':tags,
                    'genres':genres,
                    })


class BulkRetrieve(object):
    def __init__(self, clazz, limit=1000, offset=0):
        """
        @param clazz: class, one of Movie / MovieClip / Clip
        @param limit: int
        @param offset: int
        """
        if clazz==Movie or clazz==MovieClip or Clip:
            self.clazz = clazz
            self.nrow = limit
            if self.nrow < 1:
                self.nrow = 1
            self.start = offset
            if self.start < 0:
                self.start = 0
            self.end = self.start + self.nrow
        else:
            raise RuntimeError('clazz must be Clip or Movie or MovieClip')
        
    def next(self):
        """
        Return list of rows or None
        """
        rows = []
        if self.clazz == Movie:
            rows = self.clazz.objects.select_related('location').\
                                      prefetch_related('subcategory', 'manufacturers', 'directors', 'casts', 'tags',
                                                       'movies.movievector_all_movie1st', 'movies.movievector_all_movie2nd',
                                                       ).\
                                      defer('movie_name', 'last_modified')\
                                      [self.start:self.end]
            if rows:
                self.start += len(rows)
                self.end += self.nrow
        elif self.clazz == MovieClip:
            rows = self.clazz.objects.select_related('publisher', 'artist', 'topic', 'author', 'region').\
                                      prefetch_related('tags', 'genre',
                                                       'movieclips.movieclipvector_all_mv1st', 'movieclips.movieclipvector_all_mv2nd',
                                                       ).\
                                      defer('mv_name', 'last_modified')\
                                      [self.start:self.end]
            if rows:
                self.start += len(rows)
                self.end += self.nrow
        elif self.clazz == Clip:
            rows = self.clazz.objects.select_related('publisher', 'region').\
                                      prefetch_related('tags', 'genre',
                                                       'clips.clipvector_all_clip1st', 'clips.clipvector_all_clip2nd',
                                                       ).\
                                      defer('clip_name', 'last_modified')\
                                      [self.start:self.end]
            if rows:
                self.start += len(rows)
                self.end += self.nrow
        # return queryset
        return rows

def feed_movie(movieinfo):
    """
    """
    if isinstance(movieinfo, MovieInfo):
        # convert to to Movie model
        mm, fks, m2ms = movieinfo.to_movie_model()
        
        if fks['location']:
            mm.location = fks['location']
            
        if mm.save():
            for k, v in m2ms.iteritems():
                if k == 'genres' and v:
                    for i in range(len(v)):
                        mm.subcategory.add(v[i])
                elif k == 'manufacs' and v:
                    for i in range(len(v)):
                        mm.manufacturers.add(v[i])
                elif k == 'casts' and v:
                    for i in range(len(v)):
                        mm.casts.add(v[i])
                elif k == 'coworkers' and v:
                    for i in range(len(v)):
                        mm.directors.add(v[i])
                elif k == 'tags' and v:
                    for i in range(len(v)):
                        mm.tags.add(v[i])
        
def feed_movieclip(mvinfo):
    """
    """
    if isinstance(mvinfo, MovieClipInfo):
        mv, fks, m2ms = mvinfo.to_movieclip_model()
        
        for k,v in fks.iteritems():
            if k == 'publisher' and v:
                mv.publisher = v
            elif k == 'artist' and v:
                mv.artist = v
            elif k == 'topic' and v:
                mv.topic = v
            elif k == 'region' and v:
                mv.region = v
            elif k == 'author' and v:
                mv.author = v
        
        if mv.save():
            tags = m2ms['tags']
            if tags:
                for tag in tags:
                    mv.tags.add(tag)
            genres = m2ms['genres']
            if genres:
                for genre in genres:
                    mv.genre.add(genre)
                    
def feed_clip(clipinfo):
    """
    """
    if isinstance(clipinfo, ClipInfo):
        clip, fks, m2ms = clipinfo.to_clip_model()
        
        for k,v in fks.iteritems():
            if k == 'publisher' and v:
                clip.publisher = v
            elif k == 'region' and v:
                clip.region = v
        
        if clip.save():
            tags = m2ms['tags']
            if tags:
                for tag in tags:
                    clip.tags.add(tag)
            genres = m2ms['genres']
            if genres:
                for genre in genres:
                    clip.genre.add(genre)

pkeybak = 0
def get_highest_pk(clazz):
    global pkeybak
    if clazz != MovieVector and clazz != MovieClipVector and clazz != ClipVector:
        raise RuntimeError('Only support classes: MovieVector, MovieClipVector, ClipVector')
    # detect highest primary key
    try:
        if pkeybak == 0:
            q=clazz.objects.aggregate(highest_id=Max('pkey'))
            pkeybak = q['highest_id']
            if pkeybak is None:
                pkeybak = 0
        
        pkey = pkeybak
        pkeybak += 1
        return pkey
    except clazz.DoesNotExist as dne:
        raise dne

def store_movie_vector(vec):
    """
    """
    if isinstance(vec, dict):
        id = get_highest_pk(MovieVector) + 1
        movie_vec = MovieVector(pkey=id, **vec)
        movie_vec.save()
        return True
    return False

def store_movieclip_vector(vec):
    """
    """
    if isinstance(vec, dict):
        id = get_highest_pk(MovieClipVector) + 1
        mv_vec = MovieClipVector(pkey=id, **vec)
        mv_vec.save()
        return True
    return False

def bulk_store_movie_vector(vecs, start_id=0):
    """
    """
    if isinstance(vecs, list):
#        movies = []
        #id = get_highest_pk(MovieVector)
        id = start_id
        for vec in vecs:
            if isinstance(vec, dict) and filter(vec, 'movie'):
                if settings.VECTOR_ON_MONGO:
                    movie1 = vec.pop('movie1st').movieID
                    movie2 = vec.pop('movie2nd').movieID
                    movie_vec = MovieVector2(movie1st=movie1, movie2nd=movie2, **vec)
                else:
                    id += 1
                    movie_vec = MovieVector(pkey=id, **vec)
#                    movies.append(movie_vec)
                if MOVIES_QUEUE.full():
                    print 'queue full, freeze'
                    time.sleep(0.5)
                MOVIES_QUEUE.put(movie_vec)
        return True
#        if movies:
#            n_cluster = len(movies) / int(BULK_INSERT_ITEMS) + 1
#            for i in range(n_cluster):
#                offset = i*BULK_INSERT_ITEMS
#                end = offset + BULK_INSERT_ITEMS
#                cluster = movies[offset:end]
#                try:
#                    if cluster:
#                        MovieVector.objects.bulk_create(cluster)
#                except DatabaseError as dbe:
#                    print 'debug [index=%d, n_clusters=%d, n_records=%d, cluster_size=%d]' % \
#                          (i, n_cluster, len(movies), BULK_INSERT_ITEMS)
#                    raise dbe
#            return True
    return False

def bulk_store_movieclip_vector(vecs, start_id=0):
    """
    """
    if isinstance(vecs, list):
#        movieclips = []
        #id = get_highest_pk(MovieClipVector)
        id = start_id
        for vec in vecs:
            if isinstance(vec, dict) and filter(vec, 'mv'):
                if settings.VECTOR_ON_MONGO:
                    mv1 = vec.pop('mv1st').mvID
                    mv2 = vec.pop('mv2nd').mvID
                    movieclip_vec = MovieClipVector2(mv1st=mv1, mv2nd=mv2, **vec)
                else:
                    id += 1
                    movieclip_vec = MovieClipVector(pkey=id, **vec)
#                    movieclips.append(movieclip_vec)
                if MV_QUEUE.full():
                    print 'queue full, freeze'
                    time.sleep(0.5)
                MV_QUEUE.put(movieclip_vec)
        return True
#        if movieclips:
#            n_cluster = len(movieclips) / int(BULK_INSERT_ITEMS) + 1
#            for i in range(n_cluster):
#                offset = i*BULK_INSERT_ITEMS
#                end = offset + BULK_INSERT_ITEMS
#                cluster = movieclips[offset:end]
#                try:
#                    if cluster:
#                        MovieClipVector.objects.bulk_create(cluster)
#                except DatabaseError as dbe:
#                    print 'debug [index=%d, n_clusters=%d, n_records=%d, cluster_size=%d]' % \
#                          (i, n_cluster, len(movieclips), BULK_INSERT_ITEMS)
#                    raise dbe
#            return True
    return False

def bulk_store_clip_vector(vecs, start_id=0):
    """
    """
    if isinstance(vecs, list):
#        clips = []
        #id = get_highest_pk(ClipVector)
        id = start_id
        for vec in vecs:
            if isinstance(vec, dict) and filter(vec, 'clip'):
                if settings.VECTOR_ON_MONGO:
                    clip1 = vec.pop('clip1st').clipID
                    clip2 = vec.pop('clip2nd').clipID
                    clip_vec = ClipVector2(clip1st=clip1, clip2nd=clip2, **vec)
                else:
                    id += 1
                    clip_vec = ClipVector(pkey=id, **vec)
#                    clips.append(clip_vec)
                if CLIPS_QUEUE.full():
                    print 'queue full, freeze'
                    time.sleep(0.5)
                CLIPS_QUEUE.put(clip_vec)
        return True
#        if clips:
#            n_cluster = len(clips) / int(BULK_INSERT_ITEMS) + 1
#            for i in range(n_cluster):
#                offset = i*BULK_INSERT_ITEMS
#                end = offset + BULK_INSERT_ITEMS
#                cluster = clips[offset:end]
#                try:
#                    if cluster:
#                        ClipVector.objects.bulk_create(cluster)
#                except DatabaseError as dbe:
#                    print 'debug [index=%d, n_clusters=%d, n_records=%d, cluster_size=%d]' % \
#                          (i, n_cluster, len(clips), BULK_INSERT_ITEMS)
#                    raise dbe
#            return True
    return False

def store_movie_boosts(vec):
    """
    """
    if isinstance(vec, dict):
        movie_boosts = MovieVectorBoost(vec)
        movie_boosts.save()
        return True
    return False

def store_movieclip_boosts(vec):
    """
    """
    if isinstance(vec, dict):
        mv_boosts = MovieClipVectorBoost(vec)
        mv_boosts.save()
        return True
    return False

def retrieve_movie(movieId):
    """
    """
    try:
        q = Movie.objects.get(movieID=movieId)
        return q
    except:
        return None
    
def retrieve_movieclip(movieclipId):
    """
    """
    try:
        q = MovieClip.objects.get(mvID=movieclipId)
        return q
    except:
        return None
    
def retrieve_clip(clipId):
    """
    """
    try:
        q = Clip.objects.get(clipID=clipId)
        return q
    except:
        return None
    
def retrieve_movie_boosts_vector(*args):
    """
    Get the latest active movie's boost vector
    """
    try:
        #return MovieVectorBoost.objects.filter(active=True).values_list(*args)[0]
        return MovieVectorBoost.objects.filter(active=True)[0]
    except:
        return None
    
def retrieve_movieclip_boosts_vector(*args):
    """
    Get the latest active movieclip's boost vector
    """
    try:
        #return MovieClipVectorBoost.objects.filter(active=True).values_list(*args)[0]
        return MovieClipVectorBoost.objects.filter(active=True)[0]
    except:
        return None
    
def retrieve_clip_boosts_vector(*args):
    """
    Get the latest active clip's boost vector
    """
    try:
        #return ClipVectorBoost.objects.filter(active=True).values_list(*args)[0]
        return ClipVectorBoost.objects.filter(active=True)[0]
    except:
        return None
    
def store_movie_candidate(movieId, movie_candidates, **kwargs):
    name = kwargs.get('movie_name', 'n/a')
    ranking_scores = kwargs.get('scores', 'hidden')
    movie = MovieCandidates(movieID=movieId, candidates=movie_candidates, movie_name=name, scores=ranking_scores)
    movie.save()
    
def bulk_store_movie_candidate(candidates):
    if isinstance(candidates, list):
        q = MovieCandidates.objects.aggregate(highest_id=Max('pk'))
        id = q['highest_id']
        if not id:
            id = 0
        now = datetime.today()
        movies = []
        for movieId, movie_candidates, infos in candidates:
            id += 1
            name = infos.get('movie_name', 'n/a')
            ranking_scores = infos.get('scores', 'hidden')
            movie = MovieCandidates(pk=id, movieID=movieId, candidates=movie_candidates, movie_name=name, 
                                     scores=ranking_scores, last_modified=now)
            movies.append(movie)
        if movies:
            saving_time = 0.0
            n_cluster = len(movies) / int(BULK_INSERT_ITEMS) + 1
            for i in range(n_cluster):
#                offset = i*BULK_INSERT_ITEMS
#                end = offset + BULK_INSERT_ITEMS
#                cluster = movies[offset:end]
                cluster = movies[:BULK_INSERT_ITEMS]
                try:
                    if cluster:
                        ts = time.time()
                        MovieCandidates.objects.bulk_create(cluster)
                        saving_time += time.time() - ts
                        del movies[:BULK_INSERT_ITEMS]
                except DatabaseError as dbe:
                    print 'debug [index=%d, n_clusters=%d, n_records=%d, cluster_size=%d]' % \
                          (i, n_cluster, len(movies), BULK_INSERT_ITEMS)
                    #raise dbe
                    print dbe
                    pass
            movies[:] = []
            print 'saving time: %.3fs' % saving_time
            return True
    return False
    
def store_movieclip_candidate(mvId, mv_candidates, **kwargs):
    name = kwargs.get('mv_name', 'n/a')
    ranking_scores = kwargs.get('scores', 'hidden')
    mv = MovieClipCandidates(mvID=mvId, candidates=mv_candidates, mv_name=name, scores=ranking_scores)
    mv.save()
    
def bulk_store_movieclip_candidate(candidates):
    if isinstance(candidates, list):
        q = MovieClipCandidates.objects.aggregate(highest_id=Max('pk'))
        id = q['highest_id']
        if not id:
            id = 0
        now = datetime.today()
        movieclips = []
        for mvId, mv_candidates, infos in candidates:
            id += 1
            name = infos.get('mv_name', 'n/a')
            ranking_scores = infos.get('scores', 'hidden')
            mv = MovieClipCandidates(pk=id, mvID=mvId, candidates=mv_candidates, mv_name=name, 
                                     scores=ranking_scores, last_modified=now)
            movieclips.append(mv)
        if movieclips:
            saving_time = 0.0
            n_cluster = len(movieclips) / int(BULK_INSERT_ITEMS) + 1
            for i in range(n_cluster):
#                offset = i*BULK_INSERT_ITEMS
#                end = offset + BULK_INSERT_ITEMS
#                cluster = movieclips[offset:end]
                cluster = movieclips[:BULK_INSERT_ITEMS]
                try:
                    if cluster:
                        ts = time.time()
                        MovieClipCandidates.objects.bulk_create(cluster)
                        saving_time += time.time() - ts
                        del movieclips[:BULK_INSERT_ITEMS]
                except DatabaseError as dbe:
                    print 'debug [index=%d, n_clusters=%d, n_records=%d, cluster_size=%d]' % \
                          (i, n_cluster, len(movieclips), BULK_INSERT_ITEMS)
                    #raise dbe
                    print dbe
                    pass
            movieclips[:] = []
            print 'saving time: %.3fs' % saving_time
            return True
    return False
    
def store_clip_candidate(clipId, clip_candidates, **kwargs):
    name = kwargs.get('clip_name', 'n/a')
    ranking_scores = kwargs.get('scores', 'hidden')
    clip = ClipCandidates(clipID=clipId, candidates=clip_candidates, clip_name=name, scores=ranking_scores)
    clip.save()
    
    
def bulk_store_clip_candidate(candidates):
    if isinstance(candidates, list):
        q = ClipCandidates.objects.aggregate(highest_id=Max('pk'))
        id = q['highest_id']
        if not id:
            id = 0
        now = datetime.today()
        clips = []
        for clipId, clip_candidates, infos in candidates:
            id += 1
            name = infos.get('clip_name', 'n/a')
            ranking_scores = infos.get('scores', 'hidden')
            clip = ClipCandidates(pk=id, clipID=clipId, candidates=clip_candidates, clip_name=name, 
                                  scores=ranking_scores, last_modified=now)
            clips.append(clip)
        if clips:
            saving_time = 0.0
            n_cluster = len(clips) / int(BULK_INSERT_ITEMS) + 1
            for i in range(n_cluster):
#                offset = i*BULK_INSERT_ITEMS
#                end = offset + BULK_INSERT_ITEMS
#                cluster = clips[offset:end]
                cluster = clips[:BULK_INSERT_ITEMS]
                try:
                    if cluster:
                        ts = time.time()
                        ClipCandidates.objects.bulk_create(cluster)
                        saving_time += time.time() - ts
                        del clips[:BULK_INSERT_ITEMS]
                except DatabaseError as dbe:
                    print 'debug [index=%d, n_clusters=%d, n_records=%d, cluster_size=%d]' % \
                          (i, n_cluster, len(clips), BULK_INSERT_ITEMS)
                    #raise dbe
                    print dbe
                    pass
            clips[:] = []
            print 'saving time: %.3fs' % saving_time
            return True
    return False

def retrieve_movie_candidate(movieId):
    try:
        q = MovieCandidates.objects.only('candidates').values_list('candidates', flat=True)
        return q.get(movieID=movieId)
    except MovieCandidates.DoesNotExist:
        return None
    
def retrieve_movieclip_candidate(mvId):
    try:
        q = MovieClipCandidates.objects.only('candidates').values_list('candidates', flat=True)
        return q.get(mvID=mvId)
    except MovieClipCandidates.DoesNotExist:
        return None
    
def retrieve_clip_candidate(clipId):
    try:
        q = ClipCandidates.objects.only('candidates').values_list('candidates', flat=True)
        return q.get(clipID=clipId)
    except ClipCandidates.DoesNotExist:
        return None
    
def list_of(clazz, mediaType):
    """
    @param clazz:
    @param media: str, 'movie' or 'mv'
    @return a dict {'list_qs':<list of queryset>, 'count':<total of rows>}
    """
    l = None
    count = 0
    no_directors = 0
    no_casts = 0
    no_singers = 0
    no_writers = 0
    if clazz == RegionID:
        l = clazz.objects.filter(media=mediaType).only('regionID').distinct()
    elif clazz == GenreID:
        l = clazz.objects.filter(media=mediaType).only('genreID').distinct()
    elif clazz == Manufacturer:
        l = clazz.objects.filter(media=mediaType).only('manufacturer').distinct()
    elif clazz == People:
        if mediaType == 'movie':
            l = clazz.objects.filter(media=mediaType).distinct()
            no_casts = l.filter(job='cast').count()
            no_directors = l.filter(job='director').count()
        elif mediaType == 'mv':
            l = clazz.objects.filter(media=mediaType).distinct()
            no_singers = l.filter(job='singer').count()
            no_writers = l.filter(job='writer').count()
    elif clazz == Tag:
        l = clazz.objects.filter(media=mediaType).only('tags').distinct()
    elif clazz == TopicID:
        l = clazz.objects.only('topicID').distinct()
    elif clazz == Movie:
        l = clazz.objects.only('movieID').distinct()
    elif clazz == MovieClip:
        l = clazz.objects.only('mvID').distinct()
    elif clazz == Clip:
        l = clazz.objects.only('clipID').distinct()
        
    if l:
        count = len(l)
    
    return {
            'list_qs':l,
            'count':count,
            'nd':no_directors,
            'nc':no_casts,
            'ns':no_singers,
            'nw':no_writers,
            }
    
class Done(object):
    def __init__(self):
        pass
    
class DBWorker(Thread):
    def __init__(self, klass, *args, **kwargs):
        super(DBWorker, self).__init__(*args, **kwargs)
        self.klass = klass
        if klass == MovieVector:
            self.queue = MOVIES_QUEUE
        elif klass == MovieClipVector:
            self.queue = MV_QUEUE
        elif klass == ClipVector:
            self.queue = CLIPS_QUEUE
        self.items = []
        # using a counter is better than using len function
        self.counter = 0
        if not is_queue_empty(klass):
            raise RuntimeError('The QUEUE not empty!!!')
        # connect to mongo
        if settings.VECTOR_ON_MONGO:
            db = settings.DATABASES['default']['NAME']
            self.mongodb = mongo.connect(db, host=settings.MONGO_HOST, port=settings.MONGO_PORT)
        
    def run(self):
        #threshold = BULK_INSERT_ITEMS - 100
        if self.klass == MovieVector:
            if settings.VECTOR_ON_MONGO:
                CLAXX = MovieVector2
            else:
                CLAXX = MovieVector
        elif self.klass == MovieClipVector:
            if settings.VECTOR_ON_MONGO:
                CLAXX = MovieClipVector2
            else:
                CLAXX = MovieClipVector
        elif self.klass == ClipVector:
            if settings.VECTOR_ON_MONGO:
                CLAXX = ClipVector2
            else:
                CLAXX = ClipVector
            
        print '<%s> STARTED' % self.getName()
        
        while True:            
            item = self.queue.get()
            
            if isinstance(item, Done):
                if self.items:
                    print '%s: last items, flush queue...' % self.getName()
                    try:
                        #CLAXX.objects.bulk_create(self.items)
                        push_to_storage(CLAXX, self.items)
                    except IntegrityError as ie:
                        print ie
                        pass
                    except DatabaseError as dbe:
#                        print 'DEBUG'
#                        print '*'*80
#                        for o in self.items:
#                            print o
#                        print '*'*80
#                        raise dbe
                        print dbe
                        pass
                    time.sleep(1)
                    self.items[:] = []
                    self.counter = 0
                    #ITEMS_QUEUE.task_done()
                #mongo.disconnect()
                break
            
            self.items.append(item)
            self.counter += 1
            
            if self.counter > BULK_INSERT_ITEMS or self.queue.full():
                print '%s: queue full, bulk insert...' % self.getName()
                try:
                    #CLAXX.objects.bulk_create(self.items[:BULK_INSERT_ITEMS])
                    push_to_storage(CLAXX, self.items[:BULK_INSERT_ITEMS])
                except IntegrityError as ie:
                    print ie
                    pass
                except DatabaseError as dbe:
#                    print 'DEBUG'
#                    print '*'*80
#                    for o in self.items[:BULK_INSERT_ITEMS]:
#                        print o
#                    print '*'*80
#                    raise dbe
                    print dbe
                    pass
                tmp = self.items[BULK_INSERT_ITEMS:]
                del self.items[:BULK_INSERT_ITEMS]
                self.items = tmp
                time.sleep(2)
                self.counter = 0
            
            #ITEMS_QUEUE.task_done()
        print '<%s> FINISHED' % self.getName()
            
def thanks_worker(worker):
    klass = worker.klass
    if klass == MovieVector:
        MOVIES_QUEUE.put(Done())
    elif klass == MovieClipVector:
        MV_QUEUE.put(Done())
    elif klass == ClipVector:
        CLIPS_QUEUE.put(Done())
    print 'waiting to finish'
    worker.join()
    
def push_to_storage(clazz, items):
    if settings.VECTOR_ON_MONGO:
        try:
            ts = time.time()
            clazz.objects.insert(items, load_bulk=False, safe=True)
            time_insert = time.time() - ts
        except mongo.OperationError:
            raise RuntimeError('can not save data to mongodb')
    else:
        ts = time.time()
        clazz.objects.bulk_create(items)
        time_insert = time.time() - ts
    print 'bulk insert (%d records) took %.3f seconds' % (len(items), time_insert)
    
def is_queue_empty(klass):
    if klass == MovieVector:
        return MOVIES_QUEUE.qsize() == 0
    elif klass == MovieClipVector:
        return MV_QUEUE.qsize() == 0
    elif klass == ClipVector:
        return CLIPS_QUEUE.qsize() == 0
    else:
        return False
    

def retrieve_vectors(item, *features):
    """
    @param item: instance of Movie / MovieClip / Clip
    @param feature: list, list of feature sorted by order to bind to vector
    """
    if settings.VECTOR_ON_MONGO:
        if isinstance(item, Movie):
            vectorId = item.movieID
            ts = time.time()
            vec_set = MovieVector2.objects(Q(movie1st=vectorId) | Q(movie2nd=vectorId))
            time_consume = time.time() - ts
            idname1st = 'movie1st'
            idname2nd = 'movie2nd'
            #print 'vectorID %d: retrieve %d vector took %.3f second' % (vectorId, len(vec_set), time_consume)
        elif isinstance(item, MovieClip):
            vectorId = item.mvID
            ts = time.time()
            vec_set = MovieClipVector2.objects(Q(mv1st=vectorId) | Q(mv2nd=vectorId))
            time_consume = time.time() - ts
            idname1st = 'mv1st'
            idname2nd = 'mv2nd'
            #print 'vectorID %d: retrieve %d vector took %.3f second' % (vectorId, len(vec_set), time_consume)
        elif isinstance(item, Clip):
            vectorId = item.clipID
            ts = time.time()
            vec_set = ClipVector2.objects(Q(clip1st=vectorId) | Q(clip2nd=vectorId))
            time_consume = time.time() - ts
            idname1st = 'clip1st'
            idname2nd = 'clip2nd'
            #print 'vectorID %d: retrieve %d vector took %.3f second' % (vectorId, len(vec_set), time_consume)
        else:
            return ([],[],0)
        if vec_set:
            vectors = []
            item_ids = []
            for vec in vec_set:
                vec_dict = vec.__dict__.get('_data')
                
                item_vec = []
                for feature in features:
                    item_vec.append(vec_dict.get(feature))
                vectors.append(item_vec)
                
                id2nd = vec_dict.get(idname1st)
                if id2nd and int(id2nd) == vectorId:
                    id2nd = vec_dict.get(idname2nd)
                item_ids.append(id2nd)
            # vectors, ids, time consumes
            return (vectors, item_ids, time_consume)
    return ([],[],0)

        
if __name__ == "__main__":
    # test save a movie
#    for i in range(100):
#        movie = MovieInfo(12346791 + i, [1,2,3,4], ['m1', 'm2'], ['d1', 'd2'], ['c1', 'c2', 'c3'], 9876, 5, 2013, 
#                          ['tag1', 'tag2', 'tag3'], True, False, True, True, True, 8.5,
#                          {'movie_name':'name of movie',
#                           'subcates_name':['tam ly', 'hanh dong', 'hai huoc', 'tinh cam'],
#                           'location_name':'phim han xeng'})
#        feed_movie(movie)
#        
#        mv = MovieClipInfo(123456791 + i, ['tag9', 'tag8', 'tag7'], 'publisher1', 2013, 1, [1,2,3], 2, 3, 4, 
#                           123, 234, 345, 456, 98765, True, 
#                           {
#                             'mv_name': 'name of mv',
#                             'lyric': True,
#                             'artist_name': 'name of artist',
#                             'topic_name':'nhac tre',
#                             'author_name':'khong ai biet',
#                             'region_name':'V-Pop',
#                             'genres_name':['blue','jazz','R&B']
#                             })
#        feed_movieclip(mv)
#    print 'done!'
    # test bulkretrieve
#    br = BulkRetrieve(Movie)
#    while True:
#        rows = br.next()
#        if not rows:
#            break
#        # put your stuff here
#        for r in rows:
#            print r.id, r
#    
#    print list_of(People, 'mv')
    # test mongo fetch data
    from goTV_Recommender.recommend import MOVIECLIP_FEATURES
    item = MovieClip(mvID=97)
    mongo.connect(settings.DATABASES['default']['NAME'], host=settings.MONGO_HOST, port=settings.MONGO_PORT)
    vecs = retrieve_vectors(item, *MOVIECLIP_FEATURES)
    if vecs:
        for vec in vecs:
            print vec
        print 'totals %d vectors' % len(vecs)
    else:
        print 'no vector found'