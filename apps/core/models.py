import datetime
import math
import numpy as np
import mongoengine as mongo
from django.db import models
from utils.vietnamese_norm import normalize_vietnamese
from utils.levenshtein import levenshtein_dyn
from utils.similarity import similar_list_calculating, similar_number_calculating

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
    def get_or_update_movie_vector(cls, movie_id, **kwargs):
        vector, _ = cls.objects.get_or_create(movie_id=movie_id)
        for k,v in kwargs:
            if k in ['movie_id', 'movie_name', 'movie_types', 'subcates', 'directors', 'casts',
                     'locations', 'release_date', 'imdb_score', 'is_hd_movie', 'is_free_movie',
                     'view_count']:
                setattr(vector, str(k), v)
        vector.save(**kwargs)
        return vector
    
    @classmethod
    def to_movie_vector(cls):
        return cls.to_json()
        
    def save(self, *args, **kwargs):
        if not self.movie_name_norm and self.movie_name:
            # normalize movie's name
            self.__movie_name_norm()
        super(MMovieVector, self).save(*args, **kwargs)
        
    def __movie_name_norm(self):
        self.movie_name_norm = normalize_vietnamese(self.movie_name)
        
    @classmethod
    def get_vector(cls, movie_id):
        # TODO: add Redis cache support here
        try:
            return cls.objects.get(movie_id=movie_id).to_movie_vector()
        except MMovieVector.DoesNotExist:
            return None
        
        
class MMovieVectorTable(mongo.Document):
    movie_id    = mongo.IntField(unique=True)
    scores      = mongo.DictField()
    
    meta = {
        'collection': 'movie_vector_table',
        'indexes': ['movie_id',],
        'allow_inheritance': False,
    }
    
    def to_json(self):
        return {
            'movie_id': self.movie_id,
            'scores':   self.scores,
        }
        
    def __calc_movie_score(self, movie_id_1, movie_id_2, **boosts):
        movie_vector_1 = MMovieVector.get_vector(movie_id_1)
        movie_vector_2 = MMovieVector.get_vector(movie_id_2)
        if movie_vector_1 and movie_vector_2:
            features = {}
            for feature_name, feature_value_1 in movie_vector_1.iteritems():
                feature_value_2 = movie_vector_2[feature_name]
                if feature_name == 'movie_name':
                    features[feature_name] = self.__movie_name_scoring(feature_value_1, feature_value_2)
                elif feature_name == 'movie_types':
                    features[feature_name] = self.__movie_types_scoring(feature_value_1, feature_value_2)
                elif feature_name == 'subcates':
                    features[feature_name] = self.__movie_subcates_scoring(feature_value_1, feature_value_2)
                elif feature_name == 'directors':
                    features[feature_name] = self.__movie_directors_scoring(feature_value_1, feature_value_2)
                elif feature_name == 'casts':
                    features[feature_name] = self.__movie_casts_scoring(feature_value_1, feature_value_2)
                elif feature_name == 'locations':
                    features[feature_name] = self.__movie_locations_scoring(feature_value_1, feature_value_2)
                elif feature_name == 'release_date':
                    features[feature_name] = self.__movie_release_date_scoring(feature_value_1, feature_value_2)
                elif feature_name == 'imdb_score':
                    features[feature_name] = self.__movie_imdb_scoring(feature_value_1, feature_value_2)
                elif feature_name == 'is_hd_movie':
                    pass
                elif feature_name == 'is_free_movie':
                    pass
                elif feature_name == 'view_count':
                    features[feature_name] = self.__movie_view_count_scoring(feature_value_1, feature_value_2)
            
            features_vector = []
            boost_vector = []
            for k, v in boosts.iteritems():
                boost_vector.append(boosts.get(k, 0.0))
                features_vector.append(v)

            features_vector = np.asfarray(features_vector)
            boost_vector = np.asfarray(boost_vector)
            
            return np.dot(features_vector, boost_vector)
        
        return 0.0
    
    def __movie_name_scoring(self, movie_name_1, movie_name_2):
        if movie_name_1 and movie_name_2:
            return levenshtein_dyn(movie_name_1, movie_name_2)
        return 0.0
    
    def __movie_types_scoring(self, movie_types_1, movie_types_2):
        if movie_types_1 and movie_types_2:
            return similar_list_calculating(movie_types_1, movie_types_2)
        return 0.0
    
    def __movie_subcates_scoring(self, movie_subcates_1, movie_subcates_2):
        if movie_subcates_1 and movie_subcates_2:
            return similar_list_calculating(movie_subcates_1, movie_subcates_2)
        return 0.0
    
    def __movie_directors_scoring(self, movie_directors_1, movie_directors_2):
        if movie_directors_1 and movie_directors_2:
            return similar_list_calculating(movie_directors_1, movie_directors_2)
        return 0.0
    
    def __movie_casts_scoring(self, movie_casts_1, movie_casts_2):
        if movie_casts_1 and movie_casts_2:
            return similar_list_calculating(movie_casts_1, movie_casts_2)
        return 0.0
    
    def __movie_locations_scoring(self, movie_locations_1, movie_locations_2):
        if movie_locations_1 and movie_locations_2:
            return similar_list_calculating(movie_locations_1, movie_locations_2)
        return 0.0
    
    def __movie_imdb_scoring(self, movie_imdb_score_1, movie_imdb_score_2):
        if movie_imdb_score_1 and movie_imdb_score_2:
            return similar_number_calculating(movie_imdb_score_1, movie_imdb_score_2)
        return 0.0
    
    def __movie_view_count_scoring(self, movie_view_count_1, movie_view_count_2):
        if movie_view_count_1 and movie_view_count_2:
            return similar_number_calculating(movie_view_count_1, movie_view_count_2)
        return 0.0
    
    def __movie_release_date_scoring(self, movie_release_date_1, movie_release_date_2):
        if movie_release_date_1 and movie_release_date_2:
            time_delta = (movie_release_date_1 - movie_release_date_2).total_seconds()
            return int(math.fabs(time_delta))
        return 0.0
    
    @classmethod
    def add_or_update_movie_score(cls, movie_id_1, movie_id_2):
        movie_score = cls.__calc_movie_score(movie_id_1, movie_id_2)
        
        posting_list, _ = cls.objects.get_or_create(movie_id=movie_id_1)
        scores = posting_list.scores
        scores[movie_id_2] = movie_score
        posting_list.save()
        
        posting_list, _ = cls.objects.get_or_create(movie_id=movie_id_2)
        scores = posting_list.scores
        scores[movie_id_1] = movie_score
        posting_list.save()
        
        
    @classmethod
    def get_posting_list(cls, movie_id):
        try:
            return cls.objects.get(movie_id=movie_id).scores
        except MMovieVectorTable.DoesNotExist:
            return None
