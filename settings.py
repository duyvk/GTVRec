import os, sys, re
import django.http
from mongoengine import connect

# ===================
# = Server Settings =
# ===================

ADMINS = (
    ('DataMining', 'dm@dm.com'),
)

# ==========================
# = Directory Declarations =
# ==========================

CURRENT_DIR     = os.path.dirname(__file__)
GOTVRE_DIR      = CURRENT_DIR
TEMPLATE_DIRS   = (os.path.join(CURRENT_DIR, 'templates'),)
MEDIA_ROOT      = os.path.join(CURRENT_DIR, 'media')
STATIC_ROOT     = os.path.join(CURRENT_DIR, 'static')
UTILS_ROOT      = os.path.join(CURRENT_DIR, 'utils')
VENDOR_ROOT     = os.path.join(CURRENT_DIR, 'vendor')
LOG_FILE        = os.path.join(CURRENT_DIR, 'logs/gotvre.log')

# ===============
# = PYTHON PATH =
# ===============

if '/utils' not in ' '.join(sys.path):
    sys.path.append(UTILS_ROOT)

if '/vendor' not in ' '.join(sys.path):
    sys.path.append(VENDOR_ROOT)

# ===================
# = Global Settings =
# ===================

DEBUG                   = True
MANAGERS                = ADMINS
ALLOWED_HOSTS           = ['*']
TIME_ZONE               = 'Asia/Ho_Chi_Minh'
LANGUAGE_CODE           = 'vi'
SITE_ID                 = 1
USE_I18N                = True
USE_L10N                = True
USE_TZ                  = True

ENABLE_FILTER           = False
VECTOR_ON_MONGO         = True

# ===============
# = Environment =
# ===============

PRODUCTION  = GOTVRE_DIR.find('/home/dm/gotvre/release') == 0
STAGING     = GOTVRE_DIR.find('/home/dm/gotvre/staging') == 0
DEVELOPMENT = GOTVRE_DIR.find('/media/rega/Mainland/eclipse_ws/GTVRec') == 0

# ===========================
# = Django-specific Modules =
# ===========================

TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    # Uncomment the next line for simple clickjacking protection:
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

# ===========
# = Logging =
# ===========

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}

# =========================
# = Miscellaneous Setting =
# =========================

ROOT_URLCONF        = 'urls'


# ===============
# = Django Apps =
# ===============

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admin',
    #'django.contrib.admindocs',
    'commons',
    'movies',
    'movieclips',
    'clips',
    'candidates',
    'south',
)

# =========
# = Mongo =
# =========

MONGO_DB = {
    'host': '127.0.0.1:27017',
    'name': 'go_tv_recommender',
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

# ==================
# = Configurations =
# ==================

from local_settings import *

TEMPLATE_DEBUG          = DEBUG

# =========
# = Mongo =
# =========
MONGO_DB_DEFAULTS = {
    'name': 'go_tv_recommender',
    'host': '127.0.0.1:27017',
    'alias': 'default',
}
MONGO_DB = dict(MONGO_DB_DEFAULTS, **MONGO_DB)

# if MONGO_DB.get('read_preference', pymongo.ReadPreference.PRIMARY) != pymongo.ReadPreference.PRIMARY:
#     MONGO_PRIMARY_DB = MONGO_DB.copy()
#     MONGO_PRIMARY_DB.update(read_preference=pymongo.ReadPreference.PRIMARY)
#     MONGOPRIMARYDB = connect(MONGO_PRIMARY_DB.pop('name'), **MONGO_PRIMARY_DB)
# else:
#     MONGOPRIMARYDB = MONGODB
MONGODB = connect(MONGO_DB.pop('name'), **MONGO_DB)


django.http.request.host_validation_re = re.compile(r"^([a-z0-9.-_\-]+|\[[a-f0-9]*:[a-f0-9:]+\])(:\d+)?$")
