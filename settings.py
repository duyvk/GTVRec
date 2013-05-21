import os, sys
import logging
import redis
import re
import django.http
from mongoengine import connect
from utils import jammit

# ===================
# = Server Settings =
# ===================

ADMINS       = (
    ('VTCO DMTeam', 'dm.vtco@vtc.vn'),
)

SERVER_NAME  = 'gotvrecommendation'
SERVER_EMAIL = 'server@vtc.vn'
GOTVRECOMMENDATION_URL  = 'http://recommendation.tv.go.vn'
SECRET_KEY   = 'YOUR_SECRET_KEY'

# ===========================
# = Directory Declaractions =
# ===========================

CURRENT_DIR   = os.path.dirname(__file__)
GOTVRECOMMENDATION_DIR  = CURRENT_DIR
TEMPLATE_DIRS = (os.path.join(CURRENT_DIR, 'templates'),)
MEDIA_ROOT    = os.path.join(CURRENT_DIR, 'media')
# STATIC_ROOT   = os.path.join(CURRENT_DIR, 'static')
UTILS_ROOT    = os.path.join(CURRENT_DIR, 'utils')
VENDOR_ROOT   = os.path.join(CURRENT_DIR, 'vendor')
LOG_FILE      = os.path.join(CURRENT_DIR, 'logs/gotvrecommendation.log')

# ==============
# = PYTHONPATH =
# ==============

if '/utils' not in ' '.join(sys.path):
    sys.path.append(UTILS_ROOT)

if '/vendor' not in ' '.join(sys.path):
    sys.path.append(VENDOR_ROOT)

# ===================
# = Global Settings =
# ===================

DEBUG                 = False
MANAGERS              = ADMINS
TIME_ZONE             = 'Asia/Ho_Chi_Minh'
LANGUAGE_CODE         = 'en-us'
SITE_ID               = 1
USE_I18N              = False
DEBUG_ASSETS          = DEBUG
HOMEPAGE_USERNAME     = 'popular'
ALLOWED_HOSTS         = ['*']
MEDIA_URL             = '/media/'

CACHES = {
    'default': {
        'BACKEND': 'redis_cache.RedisCache',
        'LOCATION': '127.0.0.1:6379',
        'OPTIONS': {
            'DB': 6,
            'PARSER_CLASS': 'redis.connection.HiredisParser'
        },
    },
}

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# ===============
# = Enviornment =
# ===============

PRODUCTION  = GOTVRECOMMENDATION_DIR.find('/home/dm.vtco/gotvrecommendation/prod') == 0
STAGING     = GOTVRECOMMENDATION_DIR.find('/home/dm.vtco/gotvrecommendation/staging') == 0
DEVELOPMENT = GOTVRECOMMENDATION_DIR.find('/home/dm.vtco/gotvrecommendation/development') == 0

# ===========================
# = Django-specific Modules =
# ===========================

TEMPLATE_LOADERS = (
    ('django.template.loaders.cached.Loader', (
        'django.template.loaders.filesystem.Loader',
        'django.template.loaders.app_directories.Loader',
    )),
)
TEMPLATE_CONTEXT_PROCESSORS = (
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.media",
    'django.core.context_processors.request',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.gzip.GZipMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    #'apps.userinfo.middleware.TimingMiddleware',
    #'apps.userinfo.middleware.LastSeenMiddleware',
    #'apps.userinfo.middleware.SQLLogToConsoleMiddleware',
    'subdomains.middleware.SubdomainMiddleware',
    #'apps.userinfo.middleware.SimpsonsMiddleware',
    #'apps.userinfo.middleware.ServerHostnameMiddleware',
    # TODO: should be only in development mode
    'debug_toolbar.middleware.DebugToolbarMiddleware',
)

AUTHENTICATION_BACKENDS = ('django.contrib.auth.backends.ModelBackend',)

# ===========
# = Logging =
# ===========

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '[%(asctime)-12s] %(message)s',
            'datefmt': '%b %d %H:%M:%S'
        },
        'simple': {
            'format': '%(message)s'
        },
    },
    'handlers': {
        'null': {
            'level':'DEBUG',
            'class':'django.utils.log.NullHandler',
        },
        'console':{
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        },
        'log_file':{
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': LOG_FILE,
            'maxBytes': '16777216', # 16megabytes
            'formatter': 'verbose'
        },
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler',
            'filters': ['require_debug_false'],
            'include_html': True,
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['console', 'log_file'],
            'level': 'ERROR',
            'propagate': True,
        },
        'django.db.backends': {
            'handlers': ['null'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'gotvrecommendation': {
            'handlers': ['console', 'log_file'],
            'level': 'DEBUG',
            'propagate': False,
        },
    'apps': {
            'handlers': ['log_file'],
            'level': 'INFO',
            'propagate': True,
        },
    },
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
}

# ==========================
# = Miscellaneous Settings =
# ==========================

ROOT_URLCONF            = 'urls'
INTERNAL_IPS            = ('127.0.0.1',)
APPEND_SLASH            = False
SESSION_ENGINE          = "django.contrib.sessions.backends.db"
TEST_RUNNER             = "utils.testrunner.TestRunner"
SESSION_COOKIE_NAME     = 'gtvr_sessionid'
SESSION_COOKIE_AGE      = 60*60*24*365*2 # 2 years
SESSION_COOKIE_DOMAIN   = '.go.vn'

# ==============
# = Subdomains =
# ==============

SUBDOMAIN_URLCONFS = {
    None: 'urls',
    'www': 'urls',
}
REMOVE_WWW_FROM_DOMAIN = True

# ===========
# = Logging =
# ===========

LOG_LEVEL = logging.DEBUG
LOG_TO_STREAM = False

# ===============
# = Django Apps =
# ===============

INSTALLED_APPS = (
    'django.contrib.staticfiles',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.sites',
    'django.contrib.admin',
    'django_extensions',
    'djcelery',
    'apps.userinfo',
    'apps.recommendations',
    'apps.statistics',
    'utils',
    'vendor',
)

if not DEVELOPMENT:
    INSTALLED_APPS += (
        'gunicorn',
    )
else:
    INSTALLED_APPS += (
        'debug_toolbar',
    )

# ==========
# = Celery =
# ==========

# TODO: celery configuration HERE

# =========
# = Mongo =
# =========

MONGO_DB = {
    'host': '117.103.196.164:27017',
    'name': 'gotvrecommendation',
}

# ============
# = Database =
# ============

DATABASES = {
    'default': {
        'NAME': 'gotvrecommendation',
        'ENGINE': 'django.db.backends.mysql',
        'USER': 'root',
        'PASSWORD': '',
        'HOST': '127.0.0.1',
        'PORT': '3306'
    },
}

# ====================
# = Database Routers =
# ====================

class MasterSlaveRouter(object):
    """A router that sets up a simple master/slave configuration"""

    def db_for_read(self, model, **hints):
        "Point all read operations to a random slave"
        return 'slave'

    def db_for_write(self, model, **hints):
        "Point all write operations to the master"
        return 'default'

    def allow_relation(self, obj1, obj2, **hints):
        "Allow any relation between two objects in the db pool"
        db_list = ('slave','default')
        if obj1._state.db in db_list and obj2._state.db in db_list:
            return True
        return None

    def allow_syncdb(self, db, model):
        "Explicitly put all models on all databases."
        return True

# =========
# = Redis =
# =========

REDIS = {
    'host': '117.103.196.164',
}
SESSION_REDIS_DB = 5

# ==================
# = Configurations =
# ==================
try:
    from gunicorn_conf import *
except ImportError, e:
    pass

try:
    from local_settings import *
except ImportError:
    pass

COMPRESS = not DEBUG
TEMPLATE_DEBUG = DEBUG

def custom_show_toolbar(request):
    return DEBUG

DEBUG_TOOLBAR_CONFIG = {
    'INTERCEPT_REDIRECTS': False,
    'SHOW_TOOLBAR_CALLBACK': custom_show_toolbar,
    'HIDE_DJANGO_SQL': False,
    'TAG':'div',
}

# =========
# = Redis =
# =========

BROKER_BACKEND = "redis"
BROKER_URL = "redis://%s:6379/4" % REDIS['host']
CELERY_RESULT_BACKEND = BROKER_URL

# =========
# = Mongo =
# =========

MONGO_DB_DEFAULTS = {
    'name': 'gotvrecommendation',
    'host': '117.103.196.164:27017',
    'alias': 'default',
}
MONGO_DB = dict(MONGO_DB_DEFAULTS, **MONGO_DB)

MONGODB = connect(MONGO_DB.pop('name'), **MONGO_DB)

# =========
# = Redis =
# =========

REDIS_POOL = redis.ConnectionPool(host=REDIS['host'], port=6379, db=0)
REDIS_STATISTICS_POOL = redis.ConnectionPool(host=REDIS['host'], port=6379, db=3)
REDIS_SESSION_POOL = redis.ConnectionPool(host=REDIS['host'], port=6379, db=5)

JAMMIT = jammit.JammitAssets(GOTVRECOMMENDATION_DIR)

if DEBUG:
    MIDDLEWARE_CLASSES += ('utils.mongo_raw_log_middleware.SqldumpMiddleware',)
    MIDDLEWARE_CLASSES += ('utils.redis_raw_log_middleware.SqldumpMiddleware',)
    MIDDLEWARE_CLASSES += ('utils.request_introspection_middleware.DumpRequestMiddleware',)
    MIDDLEWARE_CLASSES += ('utils.exception_middleware.ConsoleExceptionMiddleware',)

django.http.request.host_validation_re = re.compile(r"^([a-z0-9.-_\-]+|\[[a-f0-9]*:[a-f0-9:]+\])(:\d+)?$")
