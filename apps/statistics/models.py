#system lib
import datetime, time
import pytz
import math
#django lib
from django.db import models
from django.utils.timezone import utc
#3rd-party lib
import mongoengine as mongo
import pyodbc as msdb

#in app
from apps.core.models import MMovieVector,MMovieVectorTable

# Create your models here.
class Movie_Statistic(mongo.Document):
    movie_id = mongo.IntField()
    source_type = mongo.IntField()
    cate = mongo.IntField()
#    release_date= mongo.DateTimeField()
#    created_date = mongo.DateTimeField()
    collected_date = mongo.DateTimeField(default=datetime.datetime.utcnow())
    view_count = mongo.ListField()
    score = mongo.DecimalField(default=0.0)
    
    meta = {
        'collection': 'movie_statistic',
        'allow_inheritance': False,
        'index_drop_dups': True,
        'shard_key':('movie_id', 'source_type','collected_date'),
        'ordering': ['source_type', 'movie_id','collected_date'],
        'app_label': 'statistics'
    }

    def __unicode__(self):
        return "Vector movie  <id=%s> <sourceType=%s> <cate=%s><date=%s><viewcount=%s>"\
            % ( self.movie_id,self.source_type,self.cate,self.collected_date,self.view_count)
    
    @classmethod
    def update_movies(cls):
        # query all viewcount statistic table
        conn_ms = msdb.connect('DRIVER=FreeTDS;SERVER=117.103.196.39;PORT=1433;DATABASE=tv.go.vn;UID=tv.go.vn;PWD=goTV!@#;TDS_Version=8.0;')
        cursor_ms = conn_ms.cursor()
    
        # Lists the tables in demo
        myGetQuery_movie = "select  Id,CategoryId,SourceType,ReleaseDate,CreateTime,\
                         ViewCount from view_ListMovies "
    
            # Execute the SQL query and get the response
        cursor_ms.execute(myGetQuery_movie)
        response = cursor_ms.fetchall()
    
        #a = cls.objects.delete()
        # Loop through the response and print table names
        for row in (response):
                        
            collected_date = datetime.datetime.now().date()#.strftime("%Y-%m-%d")#datetime.utcnow().replace(tzinfor=utc)
            
            m  = cls.objects.get_or_create(collected_date=collected_date\
                ,cate=row.CategoryId, source_type=row.SourceType, movie_id = row.Id)
            m[0].view_count.append(int(row.ViewCount))
#            m[0].release_date = row.ReleaseDate #datetime.datetime.strptime(row.ReleaseDate, )
#            m[0].created_date = row.CreateTime
#            t1 = datetime.datetime.strptime("2013-01-01","%Y-%m-%d")
#            print (m[0].created_date.toordinal())-t1.toordinal()
            m[0].save()
    
    def created_date_score(self,thresold):
        
        return 0.0
    
    def released_date_score(self, thresold):
        if self.cate and self.movie_id and self.source_type:
            print "release_date_score"
            print self.cate, self.movie_id, self.source_type
            try:
                m = MMovieVector.objects.get(cate=self.cate, movie_id = self.movie_id, source_type=self.source_type)
                print m.release_date
            except Exception as e:
                print e
                return 0.0
        return 0.0
    
    def view_count_score(self):
        return self.view_count[-1] - self.view_count[0]
    
    def trends_score(self):
        slope = self.view_count[-1]-self.view_count[0]
        total_views = self.view_count[-1]
        try:
            trend = slope  * math.log(1.0 +int(total_views))
            error = 1.0/math.sqrt(int(total_views))
        except Exception as e:
            return 0,0
        return trend, error
    
    @classmethod
    def hot_rank(cls, **boosts):
        pass
        # for each movie
            # created_date score
            # released_date score
            # view_count score
            # trends score
            #-> calculate overral score
        # return hot_rank  
            


#class hot_rank(models.Model):
#    collected_date = models.DateTimeField()
#    last_modified = models.DateTimeField(auto_now=True)
#    cate = models.IntegerField()
#    source_type = models.IntegerField()
#    hot_list = models.CharField()
#    class meta:
#        app_label = "statistics"
#        
#    def __unicode__(self):
#        return "Hot rank <category: %s> <sourceType: %s> \
#                    <lastModified: %s> \n Hot Rank: \n %s "\
#                    %(self.cate, self.source_type,self.last_modified,self.hot_list)
#    
#    def get_hot_rank(self):
#        # hot_rank
#        # creat or get now row 
#        pass
#    def put_to_upstream(self):
#        # put to Postgres
#        # put to TrungVo
#        pass
#            

if __name__ == "__main__":
    
    #Movie_Statistic.update_movies()
    listm = Movie_Statistic.objects.all()
    
    #MAke the MSSQL connection
    conn_ms = msdb.connect('DRIVER=FreeTDS;SERVER=117.103.196.39;PORT=1433;DATABASE=tv.go.vn;UID=tv.go.vn;PWD=goTV!@#;TDS_Version=8.0;')
    
    cursor_ms = conn_ms.cursor()
    trancate_movie = "delete from dbo.MiningHot";
    cursor_ms.execute(trancate_movie);
    for m in listm:
        #m.released_date_score(0.1)
        #print m.view_count_score()
        if m.trends_score()[0] >0:
            #print m.trends_score() , m.movie_id
            

            myGetQuery_movie = "insert into dbo.MiningHot values (%d, %d,%d,%f);"\
                            %(m.cate, m.source_type,m.movie_id, m.trends_score()[0])
            print myGetQuery_movie
            cursor_ms.execute(myGetQuery_movie)
    conn_ms.close()
        
        
        
            