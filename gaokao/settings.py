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
BASE_DIR = os.path.dirname(os.path.dirname(__file__))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.7/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 's+3msph#0v4o=fvu^*i!42hrp^w5(j6sr#kis@)=8^q3p3=+*m'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = []


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
    'compressor', # django_compressor
    'django_filters', # django-filters
    'tagging', # django-tagging
    'pagination', # django-pagination
    'crispy_forms', # django-crispy-forms
    'bootstrap3', # django-bootstrap3
    'pi', 
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'pagination.middleware.PaginationMiddleware', # django-pagination
)

ROOT_URLCONF = 'gaokao.urls'

WSGI_APPLICATION = 'gaokao.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.7/ref/settings/#databases

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
	'/var/www/static/',
)
MEDIA_ROOT = '/home/fengxia/Desktop/tt'
STATIC_ROOT='/var/www/static'

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
COMPRESS_PRECOMPILERS = (
    ('text/x-scss', 'django_libsass.SassCompiler'),
)