from django.db import models
from datetime import datetime
from raven.conf.defaults import MAX_LENGTH_LIST


GOTV_MEDIA_TYPE=(
    ('movie', _('MOVIE')),
    ('mv', _('MOVIE_CLIP')),
    ('clip', _('CLIP')),
)

GOTV_JOBS=(
    ('director', 'DIRECTOR'),
    ('cast', 'CAST'),
    ('writer', 'WRITER'),
    ('singer', 'SINGER'),
)


class Movie(models.Model):
    '''
    Movie table
    '''
    movie_id = models.IntegerField(db_index=True)
    source_type = models.IntegerField()
    
    movie_name = models.CharField(max_length=100, blank=True)
    
    subcates = models.ManyToManyField(GenreID, blank=True, null=True)
    subcates_name = models.CharField(max_length=100, blank=True)
    #manufacturers = models.ManyToManyField(Manufacturer, blank=True, null=True)

    
    directors = models.ManyToManyField(People, blank=True, null=True,
                                       related_name='%(app_label)s_%(class)s_directed')
    casts = models.ManyToManyField(People, blank=True, null=True,
                                   related_name='%(app_label)s_%(class)s_acted')

    #size = models.IntegerField(default=0, verbose_name=_('movie duration'), help_text=_('movie duration'))

   
    location = models.ForeignKey(RegionID, blank=True, null=True, on_delete=models.SET_NULL)
    
    IMDB_score = models.FloatField(blank=True, null=True)
    
    release_date = models.DateTimeField()
    release_year = models.IntegerField(blank=True, null=True)

    is_HD = models.BooleanField(default=False)
    is_free = models.BooleanField(default=True)
    is_single_movie = models.BooleanField(default=True)

    movie_type = models.CharField(max_length=20, blank=True, null=True, choices=GOTV_MOVIE_TYPE)
    
    #tags = models.ManyToManyField(Tag, blank=True, null=True)

    # added
    image_url = models.CharField(max_length=200, blank=True)

    # added
    view_count = models.IntegerField(default=0)

    #last_modified = models.DateTimeField(auto_now=True)

    

class GenreID(models.Model):
    """
    Movie: subcategoryID
    MovieClip, Clip: genreID
    """
    genreID = models.IntegerField(db_index=True)
    
    genre_name = models.CharField(max_length=50, blank=True)
    
    #media = models.CharField(max_length=20, choices=GOTV_MEDIA_TYPE, db_index=True)
    
    def __unicode__(self):
        name = unicode(self.genreID)
        if self.genre_name:
            name = self.genre_name
        return u'%s_%s' % (name, self.media)
    
class Manufacturer(models.Model):
    """
    Movie: Manufacturer
    MovieClip, Clip: Publisher
    """
    manufacturer = models.CharField(max_length=200, db_index=True)
    
    #media = models.CharField(max_length=20, choices=GOTV_MEDIA_TYPE, db_index=True)
    
    def __unicode__(self):
        return u'%s_%s' % (self.manufacturer, self.media)
    
class People(models.Model):
    """
    Movie: requires `person_name`, MovieClip also requires person_name
    MovieClip: requires `personID`
    """
    person_name = models.CharField(max_length=200, db_index=True,
        help_text=_('required by Movie/MovieClip/Clip'))
    
    personID = models.IntegerField(blank=True, null=True, db_index=True,
        help_text=_('person name should be associated with a ID'))
    
    job = models.CharField(max_length=20, choices=GOTV_JOBS, db_index=True)
    
    #media = models.CharField(max_length=20, choices=GOTV_MEDIA_TYPE, db_index=True)
    
    def __unicode__(self):
        return u'%s' % (self.person_name)
    
    @models.permalink
    def get_absolute_url(self):
        pass
    #    return ('people',(),{'pk':self.personId})
    
    
class RegionID(models.Model):
    """
    Movie: LocationID
    MovieClip, Clip: RegionID
    """
    regionID = models.IntegerField(db_index=True)
    
    region_name = models.CharField(max_length=200, blank=True)
    
    #media = models.CharField(max_length=20, choices=GOTV_MEDIA_TYPE, db_index=True)
    
    def __unicode__(self):
        name = unicode(self.regionID)
        if self.region_name:
            name = self.region_name
        return u'%s_%s' % (name, self.media)
    
    
# Create your models here.
#class Tag(models.Model):
#    """
#    Movie: tags
#    MovieClip: tags
#    Clip: tags
#    """
#    tags = models.CharField(max_length=200, blank=True, db_index=True)
#    
#    media = models.CharField(max_length=20, choices=GOTV_MEDIA_TYPE, db_index=True)
#    
#    def __unicode__(self):
#        return u'%s_%s' % (self.tags, self.media)
    

#class TopicID(models.Model):
#    """
#    MovieClip
#    """
#    topicID = models.IntegerField(db_index=True)
#    
#    topic_name = models.CharField(max_length=200, blank=True)
#    
#    def __unicode__(self):
#        name = unicode(self.topicID)
#        if self.topic_name:
#            name = self.topic_name
#        return u'%s' % (name)
