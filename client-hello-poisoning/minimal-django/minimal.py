import sys

from django.conf import settings
from django.conf.urls import url
from django.core.management import execute_from_command_line
from django.http import HttpResponse
from django.core.cache import cache as django_cache

settings.configure(
    DEBUG=True,
    ROOT_URLCONF=sys.modules[__name__],
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
            'LOCATION': '127.0.0.1:11211',
        },
    },
)

def rate_limited_sloth(request):
    was_visited = django_cache.get('page_hits', False)
    django_cache.set('page_hits', True, timeout=3)
    if was_visited:
        return HttpResponse('<h1>The sloth needs to sleep for 3 seconds.</h1>')
    return HttpResponse(u'<div style="font-size: 50vh">\U0001f9a5</div>')

urlpatterns = [
    url(r'^$', rate_limited_sloth),
]

if __name__ == '__main__':
    execute_from_command_line(sys.argv)
