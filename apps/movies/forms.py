'''
Created on May 16, 2013

@author: hieunv
'''
from django.forms.forms import Form
from django.forms.fields import CharField
class MovieWeightsForm(Form):
    subcategory = CharField()
    manufacturer = CharField()
    director = CharField()
    size = CharField()
    cast = CharField()
    location = CharField()
    release_year = CharField()
    tag = CharField()
    imdb = CharField()
    isHD = CharField()
    isPayment = CharField()
    isSingle = CharField()
    isSameType = CharField()
    names = CharField()