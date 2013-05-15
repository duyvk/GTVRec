'''
Created on Apr 24, 2013

@author: rega
'''
# ===================
# = Global Settings =
# ===================

DEBUG = True
DEBUG_ASSETS = DEBUG
MEDIA_URL = '/media/'
SECRET_KEY          = 'r2=on24#h+!2-8004*m005p+*ej34q9jg!aq6jh_a*9oo-b63r'
WSGI_APPLICATION    = 'gotv_re.wsgi.application'

# =============
# = Databases =
# =============

DATABASES = {
    'default': {
        'NAME': 'go_tv_recommender',
        'ENGINE': 'django.db.backends.mysql',
        'USER': 'root',
        'PASSWORD': 'admin',
        'HOST': '117.103.196.164',
    },
}

MONGO_DB = {
    'name': 'go_tv_recommender',
    'host': '117.103.196.164',
    'port': 27017
}