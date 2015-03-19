# -*- coding: utf-8 -*-


"""
Django settings for jinneng project.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.7/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
from production_envvars import *

BASE_DIR = os.path.dirname(os.path.dirname(__file__))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.7/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 's+3msph#0v4o=fvu^*i!42hrp^w5(j6sr#kis@)=8^q3p3=+*m'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = DJANGO_DEBUG
TEMPLATE_DEBUG = DEBUG

ALLOWED_HOSTS = ['*']


# Application definition

																		
INSTALLED_APPS = (
	'django_admin_bootstrapped.bootstrap3',
	'django_admin_bootstrapped',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_extensions',
    # The Django sites framework is required
    'django.contrib.sites', 

    # custom packages
    'devserver', # django-devserver
    'storages', # django-storage
    's3_folder_storage', # django-s3-folder-storage
    'compressor', # django_compressor
    'django_filters', # django-filters
    'tagging', # django-tagging
    'pagination_bootstrap', # django-pagination-bootstrap
    'crispy_forms', # django-crispy-forms
    #'bootstrap3', # django-bootstrap3
    'debug_toolbar', # django-debug-toolbar
    'pi', 
)

MIDDLEWARE_CLASSES = (
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware', # django-debug-toolbar
    'pagination_bootstrap.middleware.PaginationMiddleware', # django-pagination-bootstrap
    'devserver.middleware.DevServerMiddleware',        
)

ROOT_URLCONF = 'gaokao.urls'

WSGI_APPLICATION = 'gaokao.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.7/ref/settings/#databases
if DEPLOY_TYPE == 'dev' :
    DATABASES = {
        #'default': {
        #    'ENGINE': 'django.db.backends.sqlite3',
        #    'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
        #}
    	'default': {
    		'ENGINE': 'django.db.backends.mysql', 
    		'NAME': 'gaokaopi',
    		'USER': 'root',
    		'PASSWORD': 'natalie',
    		'HOST': 'localhost',   # Or an IP Address that your DB is hosted on
    		'PORT': '3306',
    	}
    }
elif DEPLOY_TYPE=='production':
	DATABASES = {
    	#'default': {
    	#    'ENGINE': 'django.db.backends.sqlite3',
    	#    'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    	#}
        	'default': {
                	'ENGINE': 'django.db.backends.mysql', 
                	'NAME': 'gaokaopi',
                	'USER': 'fengxia',
                	'PASSWORD': 'xf123456',
                	'HOST': 'gki-db.c6nrxqagj4zh.us-east-1.rds.amazonaws.com',   # Or an IP Address that your DB is hosted on
                	'PORT': '3306',
        	}
	}

# Internationalization
# https://docs.djangoproject.com/en/1.7/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.7/howto/static-files/
STATIC_URL = '/static/'
STATICFILES_DIRS = (
	os.path.join(BASE_DIR, "static"),
)
STATICFILES_FINDERS = (
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
    'compressor.finders.CompressorFinder',
)

# crispy forms
CRISPY_TEMPLATE_PACK = 'bootstrap3'

# for django-pagination, very COOL!
from django.conf import global_settings
TEMPLATE_CONTEXT_PROCESSORS = global_settings.TEMPLATE_CONTEXT_PROCESSORS + (
		'django.core.context_processors.request',
	)

# for django-allauth
SITE_ID = 1


# LOGIN LOGOUT
LOGIN_URL ='/gaokao/login'
LOGOUT_URL ='/gaokao/home'

# libsass "pip install django-libsass"
COMPRESS_ENABLED = True
COMPRESS_CSS_FILTERS = ['compressor.filters.css_default.CssAbsoluteFilter']
COMPRESS_PRECOMPILERS = (
    ('text/x-scss', 'django_libsass.SassCompiler'),
)

# django-debug-toolbar
DEBUG_TOOLBAR_PATCH_SETTINGS = False

# django-devserver
DEVSERVER_MODULES = (
    'devserver.modules.sql.SQLRealTimeModule',
    'devserver.modules.sql.SQLSummaryModule',
    'devserver.modules.profile.ProfileSummaryModule',

    # Modules not enabled by default
    'devserver.modules.ajax.AjaxDumpModule',
    'devserver.modules.profile.MemoryUseModule',
    'devserver.modules.cache.CacheSummaryModule',
    'devserver.modules.profile.LineProfilerModule',
)
DEVSERVER_AUTO_PROFILE = False  # profiles all views without the need of function decorator

# S3 storages

if DEPLOY_TYPE =='dev':
    STATIC_ROOT='/var/www/static'
    MEDIA_ROOT = '/var/www/media'
    MEDIA_URL='http://localhost/media/'
elif DEPLOY_TYPE=='production':
    DEFAULT_FILE_STORAGE = 's3_folder_storage.s3.DefaultStorage'
    STATICFILES_STORAGE = 's3_folder_storage.s3.StaticStorage'

    DEFAULT_S3_PATH = "media"
    MEDIA_ROOT = '/%s/' % DEFAULT_S3_PATH
    MEDIA_URL = '//s3.amazonaws.com/%s/media/' % AWS_STORAGE_BUCKET_NAME

    STATIC_S3_PATH = "static"
    STATIC_ROOT = "/%s/" % STATIC_S3_PATH
    STATIC_URL = '//s3.amazonaws.com/%s/static/' % AWS_STORAGE_BUCKET_NAME
    ADMIN_MEDIA_PREFIX = STATIC_URL + 'admin/'


    #STATICFILES_STORAGE = 'storages.backends.s3boto.S3BotoStorage'
