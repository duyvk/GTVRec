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
'''
    class Meta:
        
#        model = MovieVectorBoost
#        fields = movie_fields
        fields = ['subcategory', 'manufacturer', 'director', 'size', 'cast', 'location', 'release_year', 'tag', 'imdb', 'isHD', 'isPayment', 'isSingle', 'isSameType', 'view_count', 'names']
        widgets = {
            'subcategory': TextInput(attrs={'size':'5'}),
            'manufacturer': TextInput(attrs={'size':'5', 'readonly': 'readonly', 'style': 'background-color:red'}),
            'director': TextInput(attrs={'size':'5'}),
            'size': TextInput(attrs={'size':'5'}),
            'cast': TextInput(attrs={'size':'5'}),
            'location': TextInput(attrs={'size':'5'}),
            'release_year': TextInput(attrs={'size':'5'}),
            'tag': TextInput(attrs={'size':'5', 'readonly': 'readonly', 'style': 'background-color:red'}),
            'imdb': TextInput(attrs={'size':'5'}),
            'view_count': TextInput(attrs={'size':'5'}),
            'isHD': TextInput(attrs={'size':'5'}),
            'isPayment': TextInput(attrs={'size':'5'}),
            'isSingle': TextInput(attrs={'size':'5'}),
            'isSameType': TextInput(attrs={'size':'5'}),
            'names': TextInput(attrs={'size':'5'}),
        }
'''