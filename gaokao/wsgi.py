import os,os.path
execfile('/home/ubuntu/production_envvars.py')

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
