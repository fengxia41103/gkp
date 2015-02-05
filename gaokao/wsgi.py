"""
WSGI config for gaokao project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/howto/deployment/wsgi/
"""

import os
import sys
import site

# Add the site-packages of the chosen virtualenv to work with
site.addsitedir('/home/fengxia/.virtualenvs/gaokao/local/lib/python2.7/site-packages')

# Add the app's directory to the PYTHONPATH
sys.path.append('/var/www/gkp')
sys.path.append('/var/www/gkp/gaokao')

os.environ['DJANGO_SETTINGS_MODULE'] = 'gaokao.settings'

# Activate your virtual env
activate_env=os.path.expanduser("/home/fengxia/.virtualenvs/gaokao/bin/activate_this.py")
execfile(activate_env, dict(__file__=activate_env))

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()

