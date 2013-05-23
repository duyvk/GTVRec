from django.db import models
from datetime import datetime
#from django.utils.translation import ugettext as _
#GOTV_MEDIA_TYPE=(
#    ('movie', ('MOVIE')),
#    ('mv', ('MOVIE_CLIP')),
#    ('clip', ('CLIP')),
#)

GOTV_JOBS=(
    ('director', 'DIRECTOR'),
    ('cast', 'CAST'),
    ('writer', 'WRITER'),
    ('singer', 'SINGER'),
)


class Genre(models.Model):
    """
    Movie: subcategoryID
    MovieClip, Clip: genreID
    """
    genre_id = models.IntegerField(primary_key=True)
    genre_name = models.CharField(max_length=50, blank=True)

    #media = models.CharField(max_length=20, choices=GOTV_MEDIA_TYPE, db_index=True)

    def __unicode__(self):
        if self.genre_name and self.genre_id:
            return u'%d: %s' % (self.genre_id, self.genre_name)
        else :
            return self.genre_id


    class Meta:
        app_label = 'movies'

#class Manufacturer(models.Model):
#    """
#    Movie: Manufacturer
#    MovieClip, Clip: Publisher
#    """
#    manu_id = models.AutoField(primary_key=True)
#    manufacturer = models.CharField(max_length=200, db_index=True)
#
#    #media = models.CharField(max_length=20, choices=GOTV_MEDIA_TYPE, db_index=True)
#
#    def __unicode__(self):
#        return u'%s' % (self.manufacturer)
#
#    def get_or_create_manufacturer(self,manufacturerName):
#        manufac = Manufacturer.objects.filter(manufacturer=manufacturerName)
#        if not manufac:
#            manufac = Manufacturer.objects.create(manufacturer=manufacturerName)
#            return manufac
#        return manufac[0]
#
#    class Meta:
#        app_label = 'movies'

class Artist(models.Model):
    """
    Movie: requires `person_name`, MovieClip also requires person_name
    MovieClip: requires `personID`
    """
    artist_name = models.CharField(max_length=200, db_index=True,
        help_text=('required by Movie/MovieClip/Clip'))

    #person_id = models.AutoField(primary_key=True)

    artist_job = models.CharField(max_length=40, db_index=True,null=True)

    #media = models.CharField(max_length=20, choices=GOTV_MEDIA_TYPE, db_index=True)

    def __unicode__(self):
        return (self.artist_name)

    @models.permalink
    def get_absolute_url(self):
        pass
    #    return ('people',(),{'pk':self.personId})



    class Meta:
        app_label = 'movies'

class Region(models.Model):
    """
    Movie: LocationID
    MovieClip, Clip: RegionID
    """
    region_id = models.IntegerField(primary_key=True)
    region_name = models.CharField(max_length=200, blank=True)

    #media = models.CharField(max_length=20, choices=GOTV_MEDIA_TYPE, db_index=True)

    def __unicode__(self):
        return self.region_name



    class Meta:
        app_label = 'movies'


class Movie(models.Model):
    '''
    Movie table
    '''
    movie_id = models.IntegerField(db_index=True)
    source_type = models.IntegerField(db_index=True)

    movie_name = models.CharField(max_length=100, blank=True, null=True)

    cate = models.IntegerField(null=True)

    subcates = models.ManyToManyField(Genre, blank=True, null=True)
    subcates_name = models.CharField(max_length=100, blank=True, null=True)
    #manufacturers = models.ManyToManyField(Manufacturer, blank=True, null=True)


    directors = models.ManyToManyField(Artist, blank=True, null=True,
                                       related_name='%(app_label)s_%(class)s_directed')
    casts = models.ManyToManyField(Artist, blank=True, null=True,
                                   related_name='%(app_label)s_%(class)s_acted')

    #size = models.IntegerField(default=0, verbose_name=_('movie duration'), help_text=_('movie duration'))


    location = models.ForeignKey(Region, blank=True, null=True, on_delete=models.SET_NULL)
    location_name = models.CharField(null=True,max_length=20)
    IMDB_score = models.FloatField(blank=True, null=True)

    release_date = models.DateTimeField( null=True)
    release_year = models.IntegerField(blank=True, null=True)

    is_HD = models.BooleanField(default=False)
    is_free = models.BooleanField(default=True)
    is_single_movie = models.BooleanField(default=True)

    movie_type = models.CharField(max_length=40, blank=True, null=True)

    #tags = models.ManyToManyField(Tag, blank=True, null=True)

    # added
    image_url = models.CharField(max_length=200, blank=True, null=True)

    # added
    view_count = models.IntegerField(default=0)

    #last_modified = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        name = unicode (self.movie_id)
        if self.movie_name:
            name = self.movie_name
        return u'%s'% name

#    def save(self, *args, **kwargs):
#        movie = Movie.objects.filter(movie_id=self.movie_id)\
#            .filter(source_type=self.source_type).exists()
#        if not movie:
#            super(Movie, self).save(self, *args, **kwargs)
#            return True
#        return False
#


    @models.permalink
    def get_absolute_url(self):
        pass
    #    return ('movie',(),{'source_type':self.source_type,'id':self.movie_id})

    class Meta:
        app_label = 'movies'



#TO DO
#    fix get_or_create function

if __name__ == "__main__":
    a = Genre(genre_id=1,genre_name="a")
    a.genre_name="test"
    a.save()
    b= Genre.objects.all()
    print b[0]


