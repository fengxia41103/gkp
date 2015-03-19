import os,os.path

os.environ['DJANGO_SETTINGS_MODULE'] = 'gaokao.settings'

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()



