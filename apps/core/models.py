import datetime
import mongoengine as mongo
from django.db import models
from utils.vietnamese_norm import normalize_vietnamese

class MMovieVector(mongo.Document):
    movie_id        = mongo.IntField(unique=True)
    movie_name      = mongo.StringField(default='movie')
    movie_name_norm = mongo.StringField(default='movie')
    movie_types     = mongo.ListField(mongo.StringField())
    subcates        = mongo.ListField(mongo.IntField())
    directors       = mongo.ListField(mongo.IntField())
    casts           = mongo.ListField(mongo.IntField())
    locations       = mongo.ListField(mongo.IntField())
    release_date    = mongo.DateTimeField()
    imdb_score      = mongo.FloatField()
    is_hd_movie     = mongo.BooleanField()
    is_free_movie   = mongo.BooleanField()
    view_count      = mongo.IntField(default=0)
    
    modified_date   = mongo.DateTimeField(default=datetime.datetime.utcnow())
    
    meta = {
        'collection': 'movie_vector_space',
        'allow_inheritance': False,
        'index_drop_dups': True,
    }
    
    def __unicode__(self):
        return "Vector movie %s <id=%s>" % (self.movie_name, self.movie_id)
    
    def to_json(self):
        return {
            'movie_id':     self.movie_id,
            'movie_name':   self.movie_name_norm,
            'movie_types':  [t.strip().lower() for t in self.movie_types] if self.movie_types else None,
            'subcates':     [cate for cate in self.subcates] if self.subcates else None,
            'directors':    [director for director in self.directors] if self.directors else None,
            'casts':        [cast for cast in self.casts] if self.casts else None,
            'locations':    [location for location in self.locations] if self.locations else None,
            'release_date': self.release_date,
            'imdb_score':   self.imdb_score,
            'is_hd_movie':  self.is_hd_movie,
            'is_free_movie':self.is_free_movie,
            'view_count':   self.view_count,
        }
        
    @classmethod
    def add_or_update_movie_vector(cls, movie_id, **kwargs):
        vector, created = cls.objects.get_or_create(movie_id=movie_id)
        if created:
            for k,v in kwargs:
                if k in ['movie_id', 'movie_name', 'movie_types', 'subcates', 'directors', 'casts',
                         'locations', 'release_date', 'imdb_score', 'is_hd_movie', 'is_free_movie',
                         'view_count']:
                    setattr(vector, str(k), v)
            vector.save(**kwargs)
        return vector
        
    def save(self, *args, **kwargs):
        if not self.movie_name_norm and self.movie_name:
            # TODO: normalize movie's name
            self.__movie_name_norm()
        super(MMovieVector, self).save(*args, **kwargs)
        
    def __movie_name_norm(self):
        self.movie_name_norm = normalize_vietnamese(self.movie_name)