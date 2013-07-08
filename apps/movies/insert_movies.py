'''
Created on Mar 22, 2013

@author: kidio
'''

import pyodbc as msdb
from utils.connection import SQL_connection
from datetime import datetime
from django.db import models
from apps.movies.models import Movie, Genre, Region, Artist,GOTV_JOBS
from apps.core.models import MMovieVector, MMovieVectorTable
import mongoengine as mongo
import local_settings
from utils import vietnamese_norm

# category code
CLIP_CATE_CODE = 5
MOVIE_CATE_COTE = 2
MUSIC_MVCLIP_CATE_CODE = 4
SOURCE_TYPE_CODE = 1


def get_or_create_genre(genreId, genreName):
    genre = Genre.objects.filter(genre_id=int(genreId))
    if not genre:
        genre = Genre.objects.create(genre_id=int(genreId),genre_name=genreName)
        return genre
    return genre[0]

def get_or_create_artist(personName, hisJob):
    artist = Artist.objects.filter(artist_name=personName,artist_job=hisJob)
    if not artist:
        artist = Artist.objects.create(artist_name=personName,artist_job=hisJob)
        return artist
    return artist[0]

def get_or_create_movie( movieID, sourcetype):
    movie = Movie.objects.filter(movie_id=int(movieID),source_type=sourcetype)
    if not movie:
        movie = Movie.objects.create(movie_id=int(movieID),source_type=sourcetype)
        return movie
    return movie[0]


def get_or_create_region(id,name):
    region = Region.objects.filter(region_id=id)
    if not region:
        region = Region.objects.create(region_id=id,region_name=name)
        return region
    return region[0]


def convert_str_2_list(datum, separator, clazz):
    """
    @param datum: str
    @param separator: str
    @param clazz: int or str or anything convertable
    """
    list_fields = []
    if datum:
        list_fields = datum.split(separator)
    fields = []
    for field in list_fields:
        temp = field.strip()
        if temp and temp.upper() != 'NULL':
            if temp[0] == '[' and temp[-1] == ']':
                temp = temp[1:-1]
            fields.append(clazz(temp))
    return fields

def to_list_int(datum, separator=','):
    return convert_str_2_list(datum, separator, int)

def to_list_string(datum, separator=','):
    return convert_str_2_list(datum, separator, unicode)


def insert_one_movie_row(movie_dict):

    try:
        movieID = int(movie_dict['Id'])
        sourcetype = int(movie_dict['SourceType'])
        #movie = Movie(movie_id=movieID, source_type=sourcetype)
        movie=get_or_create_movie(movieID, sourcetype)

        if   "CategoryId" in movie_dict:
            movie.cate = int(str(movie_dict['CategoryId']).strip())
        
        if "Name" in movie_dict:
            movie.movie_name = movie_dict["Name"]
            movie.save()
#        
        if "SubCategoryId" in movie_dict and "SubCategoryName" in movie_dict:
            movie.subcates_name = str(movie_dict['SubCategoryName']).strip()
            #movie.save()
            sub_cate_dict = dict(zip(to_list_int(movie_dict['SubCategoryId'],','), to_list_string(movie_dict['SubCategoryName'],',')))
            for key in sub_cate_dict:
                temp = get_or_create_genre(key,sub_cate_dict[key])
                movie.subcates.add(temp)

#
##        if "ManufacturerName" in movie_dict:
##            movie.ManufacturerName = movie_dict["ManufacturerName"]
#
        if "Imdb" in movie_dict:
            movie.IMDB_score = movie_dict["Imdb"]
            #movie.save()
        
        if "direction" in movie_dict:
            directors = to_list_string(movie_dict["direction"])
            for director in directors:
                movie.directors.add(get_or_create_artist(director, "DIRECTOR"))
            #movie.save()
        
        
        if "Actor" in movie_dict:
            casts = to_list_string(movie_dict["Actor"].strip())
            for p in casts:
                movie.casts.add(get_or_create_artist(p, "CAST"))
        
        if "LocationId" in movie_dict and  "LocationName" in movie_dict:
            movie.locatio_name = str(movie_dict["LocationName"]).strip()
            movie.location = get_or_create_region(int(movie_dict["LocationId"]),movie_dict["LocationName"])
            
        if "IsHd" in movie_dict:
            if movie_dict["IsHd"] ==1:
                movie.is_HD = True
            else :
                movie.is_HD = False
        
        if "Payment" in movie_dict:
            isPay = int(str(movie_dict["Payment"]).strip())
            if isPay == 0:
                movie.is_free = True
            else:
                movie.is_free = False
            #movie.save()
       
        if "ReleaseDate" in movie_dict:
            movie.release_date = datetime.strptime(str(movie_dict["ReleaseDate"]).split(" ")[0], "%Y-%m-%d")
            #movie.save()
            
        if "ReleaseYear" in movie_dict:
            movie.release_year = int (str(movie_dict["ReleaseYear"]).strip())
        if "MovieTypeName" in movie_dict:
            movie.movie_type = str(movie_dict['MovieTypeName']).strip()
        
        if "ImageUrl" in movie_dict:
            movie.image_url =  str(movie_dict["ImageUrl"]).strip()

        
        if "MovieTypeId" in movie_dict:
            mtype = int(str(movie_dict["MovieTypeId"]).strip())
            if mtype == 1:
                movie.is_single_movie = True
            else:
                movie.is_single_movie = False
                
        if "ViewCount" in movie_dict:
            movie.view_count = int(str(movie_dict["ViewCount"]).strip())

        movie.save()
    except Exception as e:
        raise RuntimeError(e)

def import_movie():

    #MAke the MSSQL connection
    conn_ms = SQL_connection()
    cursor_ms = conn_ms.cursor()

    # Lists the tables in demo
    myGetQuery_movie = "select  * from view_ListMovies "

    # Execute the SQL query and get the response
    cursor_ms.execute(myGetQuery_movie)
    response = cursor_ms.fetchall()

    list_colums = []
    for row in cursor_ms.columns(table='view_ListMovies'):
        list_colums.append(str(row.column_name))

    # Loop through the response and print table names
    for index, row in enumerate(response):
        
        movie_dict = dict(zip(list_colums,row))
        #movie_dict = dict ((value,row[x]) for x,value in enumerate(list_colums))
#        for key in movie_dict:
#            print key
#            print movie_dict[key]
#            print "###############"
    #    dicta = dict((list_colums[key],str(value))for key, value in enumerate(row))
    #        print list_colums[key]
    #        print str(value)
    #        print "-----"
    #    print dicto
#        print movie_dict["Id"]
#        print movie_dict["SourceType"]
#        print movie_dict
        print index
        #print "\n".join(unicode(x) for x in row)
        insert_one_movie_row(movie_dict)
#        print "cate: %s"% movie.cate
#        print "subcate:"
#        print movie.subcates_name
#        print "name"
#        print movie.movie_name
#        print "imdb"
#        print movie.IMDB_score
        
    conn_ms.close()

# transfering movies data from postgres to mongodb
def P2M_transfering_all_movies():
    mongo.connect(local_settings.MONGO_DB['name'], host=local_settings.MONGO_DB["host"], port=local_settings.MONGO_DB["port"])
    list_of_movies = Movie.objects.all()
    
    for p_movie in list_of_movies:
        m_movie = P2M_movie_object(p_movie)
        if m_movie:
#            print m_movie.movie_id
#            print m_movie.movie_name 
#            print m_movie.movie_name_norm 
#            print m_movie.movie_type 
#            print m_movie.cate 
#            print m_movie.subcates
#            print m_movie.directors
#            print m_movie.casts 
#            print m_movie.location
#            print m_movie.release_date
#            print m_movie.imdb_score 
#            print m_movie.view_count
            MMovieVector.objects.insert(m_movie)
    
# transfering a movie data from postgres to mongodb
def P2M_movie_object (p_movie):
    if p_movie.movie_id and p_movie.source_type:
        m_movie =  MMovieVector.objects.get_or_create(movie_id= p_movie.movie_id,source_type=p_movie.source_type, auto_save=False)[0]
        m_movie.movie_name = (p_movie.movie_name)
        m_movie.movie_name_norm = vietnamese_norm.normalize_vietnamese(p_movie.movie_name)
        #m_movie.movie_type = p_movie.movie_type
        m_movie.cate = p_movie.cate
        m_movie.subcates = list (subcate.genre_id for subcate in p_movie.subcates.all())
        m_movie.directors = list (director.id for director in p_movie.directors.all())
        m_movie.casts = list (actor.id for actor in p_movie.casts.all())
        m_movie.location = p_movie.location.region_id
        m_movie.release_date = p_movie.release_date
        m_movie.imdb_score = p_movie.IMDB_score
        m_movie.view_count = p_movie.view_count
        m_movie.is_HD = p_movie.is_HD
        m_movie.is_free = p_movie.is_free
        m_movie.is_single_movie = p_movie.is_single_movie 
        return m_movie
    else :
        return None

def update_movie():
    # connect tv.go.vn.MiningChange  in 117.103.196.39
    # update postgre
    # update mongo
    # recalculate everything
    pass

if __name__ == '__main__':
    
    #import movie from SQL server to postgres
    #import_movie()
    
    # import movie from postgres to mongodb(MMovieVector)
    #P2M_transfering_all_movies()
    
    
    list_of_mongo_movies = MMovieVector.objects.all()
    for m in list_of_mongo_movies:
        print m.to_movie_vector()
    print len(list_of_mongo_movies)
