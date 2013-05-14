import os
import logging

# ===================
# = Server Settings =
# ===================

ADMINS                = (
    ('Rega Ng', 'tu.nguyen2@vtc.vn'),
)

SERVER_EMAIL          = 'server@vtc.vn'
GOTVRECOMMENDATION_URL = 'http://dev.tv.go.vn'

# ===================
# = Global Settings =
# ===================

DEBUG = True
DEBUG_ASSETS = DEBUG
MEDIA_URL = '/media/'
SECRET_KEY = '@#vv441q#_a1^mrfo!zel#idh@!9x01_+=+b@fk7b%ff%0)2=5'

# =============
# = Databases =
# =============

DATABASES = {
    'default': {
        'NAME': 'gotvrecommendation',
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'USER': 'postgres',
        'PASSWORD': '',
        'HOST': '127.0.0.1',
        'PORT': '5432',
    },
}

MONGO_DB = {
    'name': 'gotvrecommendation',
    'host': '127.0.0.1',
    'port': 27017
}

# Celery RabbitMQ/Redis Broker
BROKER_URL = "redis://127.0.0.1:6379/0"
CELERY_RESULT_BACKEND = BROKER_URL

REDIS = {
    'host': '127.0.0.1',
}

# ===========
# = Logging =
# ===========

# Logging (setup for development)
LOG_TO_STREAM = True

if len(logging._handlerList) < 1:
    LOG_FILE = os.path.join(os.path.dirname(__file__), 'logs/development.log')
    logging.basicConfig(level=logging.DEBUG,
                            format='%(asctime)-12s: %(message)s',
                            datefmt='%b %d %H:%M:%S',
                            handler=logging.StreamHandler)