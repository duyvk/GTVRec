#system lib
import datetime, time

#django lib
from django.db import models

#3rd-party lib
import mongoengine as mongo


# Create your models here.
class MMovie_View_Count_Statistic(mongo.Document):
    movie_id = mongo.IntField()
    source_type = mongo.IntField()
    cate = mongo.IntField()
    release_date= mongo.DateTimeField()
    created_date = mongo.DateTimeField()
    collected_date = mongo.DateTimeField(default=datetime.datetime.utcnow())
    view_count = mongo.ListField()
    
    meta = {
        'collection': 'movie_viewcount_statistic',
        'allow_inheritance': False,
        'index_drop_dups': True,
        'shard_key':('movie_id', 'source_type','collected_date'),
        'ordering': ['source_type', 'movie_id','collected_date']
    }

    def __unicode__(self):
        return "Vector movie  <id=%s> <sourceType=%s> <date=%s>"\
            % ( self.movie_id,self.source_type,self.collected_date)
    
    @classmethod
    def update_movies(cls):
        pass
        # query all viewcount statistic table
        #query sql db
            # get the row with id
            # update it viewcount to specific date
            
    def hot_rank(self):
        pass
        
        