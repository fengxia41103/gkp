import sys,os,os.path,site

# Add the site-packages of the chosen virtualenv to work with
site.addsitedir('/home/fengxia/.virtualenvs/gaokao/local/lib/python2.7/site-packages')

# Add the app's directory to the PYTHONPATH
sys.path.append('/home/fengxia/workspace/gkp')
sys.path.append('/home/fengxia/workspace/gkp/gaokao')

os.environ['DJANGO_SETTINGS_MODULE'] = 'gaokao.settings'

# Activate your virtual env
activate_env=os.path.expanduser("~/.virtualenvs/gaokao/bin/activate_this.py")
execfile(activate_env, dict(__file__=activate_env))

# Fix django closing connection to MemCachier after every request (#11331)
# http://blog.memcachier.com/2014/12/12/django-persistent-memcached-connections/
from django.core.cache.backends.memcached import BaseMemcachedCache
BaseMemcachedCache.close = lambda self, **kwargs: None

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()


