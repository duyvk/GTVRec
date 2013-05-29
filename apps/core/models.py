import datetime,time
import math
import numpy as np
import mongoengine as mongo
from mongoengine.base import ValidationError
from django.db import models
from utils.vietnamese_norm import normalize_vietnamese
from utils.levenshtein import levenshtein_dyn
from utils.similarity import similar_list_calculating, similar_number_calculating
from apps.movies.models import Movie
import local_settings
from utils import Timer
from babel.localedata import list
from django.utils.itercompat import product
mongo.connect(local_settings.MONGO_DB['name'], host=local_settings.MONGO_DB["host"], port=local_settings.MONGO_DB["port"])

class MMovieVector(mongo.Document):
    movie_id = mongo.IntField()
    source_type = mongo.IntField()
    movie_name = mongo.StringField(default='movie')
    movie_name_norm = mongo.StringField(default='movie')
    # movie_type      = mongo.StringField()
    cate = mongo.IntField()
    subcates = mongo.ListField(mongo.IntField())
    directors = mongo.ListField(mongo.IntField())
    casts = mongo.ListField(mongo.IntField())
    location = mongo.IntField()
    release_date = mongo.DateTimeField()
    imdb_score = mongo.FloatField()
    is_HD = mongo.BooleanField()
    is_free = mongo.BooleanField()
    is_single_movie = mongo.BooleanField()
    view_count = mongo.IntField(default=0)

    modified_date = mongo.DateTimeField(default=datetime.datetime.utcnow())

    meta = {
        'collection': 'movie_vector_space',
        'allow_inheritance': False,
        'index_drop_dups': True,
        'shard_key':('movie_id', 'source_type'),
        'ordering': ['source_type', 'movie_id']
    }

    def __unicode__(self):
        return "Vector movie %s <id=%s>" % (self.movie_name, self.movie_id)

    def to_json(self):
        return {
            'movie_id':     self.movie_id,
            'source_type':  self.source_type,
            'cate':         self.cate,
            'movie_name':   self.movie_name_norm,
            # 'movie_types':  [t.strip().lower() for t in self.movie_types] if self.movie_types else None,
            'subcates':     [cate for cate in self.subcates] if self.subcates else None,
            'directors':    [director for director in self.directors] if self.directors else None,
            'casts':        [cast for cast in self.casts] if self.casts else None,
            'location':     self.location,  # [location for location in self.locations] if self.locations else None,
            'release_date': self.release_date,
            'imdb_score':   self.imdb_score,
            'is_HD':  self.is_HD,
            'is_free':self.is_free,
            'is_single_movie':  self.is_single_movie,
            'view_count':   self.view_count,
        }

    @classmethod
    def get_or_update_movie_vector(cls, movie_id, source_type, **kwargs):
        vector, _ = cls.objects.get_or_create(movie_id=movie_id, source_type=source_type)
        for k, v in kwargs:
            if k in ['movie_id', 'source_type', 'cate', 'movie_name' , 'subcates', 'directors', 'casts',
                     'location', 'release_date', 'imdb_score', 'is_HD', 'is_free', 'is_single_movie'
                     'view_count']:
                setattr(vector, str(k), v)
        vector.save(**kwargs)
        return vector

    # @classmethod
    def to_movie_vector(self):
        return self.to_json()

    def save(self, *args, **kwargs):
        if not self.movie_name_norm and self.movie_name:
            # normalize movie's name
            self.__movie_name_norm()
        super(MMovieVector, self).save(*args, **kwargs)

    def __movie_name_norm(self):
        self.movie_name_norm = normalize_vietnamese(self.movie_name)

    @classmethod
    def get_vector(cls, movie_id, source_type):
        # TODO: add Redis cache support here
        try:
            return cls.objects.get(movie_id=movie_id, source_type=source_type).to_movie_vector()
        except MMovieVector.DoesNotExist:
            return None
    
    
        


# if __name__ == "__main__":
#    pass
#    mongo.connect(local_settings.MONGO_DB['name'], host=local_settings.MONGO_DB["host"], port=local_settings.MONGO_DB["port"])
#    m = MMovieVector(movie_id= 437312,source_type=10)
#    m.movie_name      = "testmovie"
#    #m.save()
#    MMovieVector.objects.insert(m)
#
#    a = MMovieVector.objects.first()
#    a.movie_name = "xxxxxx"
#    a.save()
#
#    b = MMovieVector.objects.first()
#    print b




class MMovieVectorTable(mongo.Document):
    movie_id = mongo.IntField(unique=True)
    scores = mongo.DictField()
    created_date = mongo.DateTimeField(default=datetime.datetime.utcnow())

    meta = {
        'collection': 'movie_vector_table',
        'indexes': ['movie_id', ],
        'allow_inheritance': False,
    }

    def to_json(self):
        return {
            'movie_id': self.movie_id,
            'scores':   self.scores,
        }
    
    
    @classmethod
    def calc_movie_score(cls, movie_id_1, movie_id_2, **boosts):
        movie_vector_1 = MMovieVector.get_vector(movie_id_1, 1)
        movie_vector_2 = MMovieVector.get_vector(movie_id_2, 1)
        if movie_vector_1 and movie_vector_2:
            features = {}
            for feature_name, feature_value_1 in movie_vector_1.iteritems():
                if feature_name in boosts:
                    feature_value_2 = movie_vector_2[feature_name]
                    if feature_name == 'movie_name':
                        features[feature_name] = cls.movie_name_scoring(feature_value_1, feature_value_2)
    #                elif feature_name == 'movie_types':
    #                    features[feature_name] = self.movie_types_scoring(feature_value_1, feature_value_2)
                    elif feature_name == 'subcates':
                        features[feature_name] = cls.movie_subcates_scoring(feature_value_1, feature_value_2)
                    elif feature_name == 'directors':
                        features[feature_name] = cls.movie_directors_scoring(feature_value_1, feature_value_2)
                    elif feature_name == 'casts':
                        features[feature_name] = cls.movie_casts_scoring(feature_value_1, feature_value_2)
                    elif feature_name == 'location':
                        features[feature_name] = cls.movie_location_scoring(feature_value_1, feature_value_2)
                    elif feature_name == 'release_date':
                        # 100 years * 365 . if the difference is larger than 100 years, the value will be set to 0
                        features[feature_name] = cls.movie_release_date_scoring(100*365,feature_value_1, feature_value_2)
                    elif feature_name == 'imdb_score':
                        # maximum of imdb score is 10
                        features[feature_name] = cls.movie_imdb_scoring(10,feature_value_1, feature_value_2)
                    elif feature_name == 'is_HD':
                        pass
                    elif feature_name == 'is_free':
                        pass
                    elif feature_name == 'is_single_movie':
                        pass
                    elif feature_name == 'view_count':
                        features[feature_name] = cls.movie_view_count_scoring(feature_value_1, feature_value_2)

#            features_vector = []
#            boost_vector = []
            result = 0
            for k, v in features.iteritems():
                #boost_vector.append(boosts.get(k, 0.0))
                #features_vector.append(v)
#                print k
#                print v
#                print boosts[k]
#                print "---"
                result += boosts[k]*v
                
            return result

        return 0.0
    @classmethod
    def calc_2movie_score(cls, movie_1, movie_2, **boosts):
    
        movie_vector_1 = movie_1#.to_movie_vector()
        movie_vector_2 = movie_2#.to_movie_vector()
    
        if movie_vector_1 and movie_vector_2:
            features = {}
            for feature_name, feature_value_1 in movie_vector_1.iteritems():
                if feature_name in boosts:
                    feature_value_2 = movie_vector_2[feature_name]
                    if feature_name == 'movie_name':
                        features[feature_name] = cls.movie_name_scoring(feature_value_1, feature_value_2)
    #                elif feature_name == 'movie_types':
    #                    features[feature_name] = self.movie_types_scoring(feature_value_1, feature_value_2)
                    elif feature_name == 'subcates':
                        features[feature_name] = cls.movie_subcates_scoring(feature_value_1, feature_value_2)
                    elif feature_name == 'directors':
                        features[feature_name] = cls.movie_directors_scoring(feature_value_1, feature_value_2)
                    elif feature_name == 'casts':
                        features[feature_name] = cls.movie_casts_scoring(feature_value_1, feature_value_2)
                    elif feature_name == 'location':
                        features[feature_name] = cls.movie_location_scoring(feature_value_1, feature_value_2)
                    elif feature_name == 'release_date':
                        # 100 years * 365 . if the difference is larger than 100 years, the value will be set to 0
                        features[feature_name] = cls.movie_release_date_scoring(100*365,feature_value_1, feature_value_2)
                    elif feature_name == 'imdb_score':
                        # maximum of imdb score is 10
                        features[feature_name] = cls.movie_imdb_scoring(10,feature_value_1, feature_value_2)
                    elif feature_name == 'is_HD':
                        pass
                    elif feature_name == 'is_free':
                        pass
                    elif feature_name == 'is_single_movie':
                        pass
                    elif feature_name == 'view_count':
                        features[feature_name] = cls.movie_view_count_scoring(feature_value_1, feature_value_2)

#            features_vector = []
#            boost_vector = []
            result = 0.0
            for k, v in features.iteritems():
                #boost_vector.append(boosts.get(k, 0.0))
                #features_vector.append(v)
#                print k
#                print v
#                print boosts[k]
#                print "#######"
                result += (boosts[k]*v)
                
            return result
        
    @classmethod
    def movie_name_scoring(cls, movie_name_1, movie_name_2):
        if movie_name_1 and movie_name_2:
            return levenshtein_dyn(movie_name_1, movie_name_2)
        return 0.0
    @classmethod
    def movie_types_scoring(cls, movie_types_1, movie_types_2):
        if movie_types_1 and movie_types_2:
            return similar_list_calculating(movie_types_1, movie_types_2)
        return 0.0
    @classmethod
    def movie_subcates_scoring(cls, movie_subcates_1, movie_subcates_2):
        if movie_subcates_1 and movie_subcates_2:
            return similar_list_calculating(movie_subcates_1, movie_subcates_2)
        return 0.0
    @classmethod
    def movie_directors_scoring(cls, movie_directors_1, movie_directors_2):
        if movie_directors_1 and movie_directors_2:
            return similar_list_calculating(movie_directors_1, movie_directors_2)
        return 0.0
    @classmethod
    def movie_casts_scoring(cls, movie_casts_1, movie_casts_2):
        if movie_casts_1 and movie_casts_2:
            return similar_list_calculating(movie_casts_1, movie_casts_2)
        return 0.0
    @classmethod
    def movie_locations_scoring(cls, movie_locations_1, movie_locations_2):
        if movie_locations_1 and movie_locations_2:
            return similar_list_calculating(movie_locations_1, movie_locations_2)
        return 0.0
    @classmethod
    def movie_location_scoring(cls, movie_location_1, movie_location_2):
        if movie_location_1 == movie_location_2:
            return 1
        else :
            return 0
    @classmethod
    def movie_imdb_scoring(cls, max_score, movie_imdb_score_1, movie_imdb_score_2):
        if movie_imdb_score_1 and movie_imdb_score_2:
            return similar_number_calculating(max_score,movie_imdb_score_1, movie_imdb_score_2)
        return 0.0
    @classmethod
    def movie_view_count_scoring(cls,  movie_view_count_1, movie_view_count_2):
        if movie_view_count_1 and movie_view_count_2:
            return similar_number_calculating(-1, movie_view_count_1, movie_view_count_2)
        return 0.0
    
    @classmethod
    def movie_release_date_scoring(cls, max_days, movie_release_date_1, movie_release_date_2):
        if movie_release_date_1 and movie_release_date_2:
            time_delta = (movie_release_date_1 - movie_release_date_2) \
                if movie_release_date_1> movie_release_date_2 else ((movie_release_date_2 - movie_release_date_1))##.days/365#total_seconds()/(24*60*60)/365
        else:
            return 0.0
        diff_days =  (float)((time_delta.days))
        
        return float(max_days-diff_days)/max_days if max_days > diff_days else 0

    @classmethod
    def add_or_update_movie_score(cls, movie_id_1, movie_id_2,movie_score):

        posting_list,_ = cls.objects.get_or_create(movie_id=movie_id_1)
        scores = posting_list.scores
        scores[str(movie_id_2)] = movie_score
        #print posting_list.scores
        try:
            posting_list.validate()
        except ValidationError as e:
            print e
        posting_list.save()
        
        
        posting_list,_ = cls.objects.get_or_create(movie_id=movie_id_2)
        scores = posting_list.scores
        scores[str(movie_id_1)] = movie_score
        try:
            posting_list.validate()
        except ValidationError as e:
            print e
        posting_list.save()
        

    @classmethod
    def get_posting_list(cls, movie_id):
        try:
            return cls.objects.get(movie_id=movie_id).scores
        except MMovieVectorTable.DoesNotExist:
            return None

class MMovie_View_Count_Statistic(mongo.Document):
    movie_id = mongo.IntField()
    source_type = mongo.IntField()
    cate = mongo.IntField()
    release_date= mongo.DateTimeField()
    created_date = mongo.DateTimeField()
    collected_date = mongo.DateTimeField(default=datetime.datetime.utcnow())

    meta = {
        'collection': 'movie_vector_space',
        'allow_inheritance': False,
        'index_drop_dups': True,
        'shard_key':('movie_id', 'source_type'),
        'ordering': ['source_type', 'movie_id']
    }

    def __unicode__(self):
        return "Vector movie %s <id=%s>" % (self.movie_name, self.movie_id)



if __name__ == "__main__":
    list_of_mmovies = MMovieVector.objects.all()
    list_of_mmovie_vectors = []
    for mm in list_of_mmovies:
        list_of_mmovie_vectors.append(mm.to_movie_vector())
#    list_of_mmovie_vectors=list_of_mmovie_vectors[1:5]
    boosts = {'movie_name':0,'subcates':0.04, 'directors':0.36, 'casts':0.36,\
                     'location':0.07, 'release_date':0.01, 'imdb_score':0.01,\
                      'is_HD':0, 'is_free':0, 'is_single_movie':0,'view_count':0.4}
    #t1 = time.time()
    for m1 , m2 in product(list_of_mmovie_vectors, list_of_mmovie_vectors):
        t1 = time.time()
        if m2['movie_id'] > m1['movie_id']:
            score = MMovieVectorTable.calc_2movie_score(m1, m2, **boosts)
            if score > 0.25:
                MMovieVectorTable.add_or_update_movie_score(m1['movie_id'], m2['movie_id'], score)
            #print "[%d - % d] : %f" %(m1['movie_id'], m2['movie_id'], score)
        #print (time.time()-t1)*1000
    list_of_results = MMovieVectorTable.objects.all()
    for i in list_of_results:
        print i.movie_id,  len(i.scores)
        