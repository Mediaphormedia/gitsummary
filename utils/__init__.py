import requests
import simplejson
from django.core.urlresolvers import reverse
from django.utils.functional import lazy
import logging

# Backported form jdano 1,4
reverse_lazy = lazy(reverse, str)


class RequestError(Exception):
    pass


class RequestNotFoundError(RequestError):
    pass


def find(f, seq):
    """Return first item in sequence where f(item) == True."""
    for item in seq:
        if f(item):
            return item

logger = logging.getLogger('django_git_summary.debug')


def request_json(*args, **kwargs):
    resp = requests.get(*args, **kwargs)
    logger.debug("%s - %s" % (resp.status_code, resp.url))
    if resp.status_code == 200:
        return simplejson.loads(resp.content)
    elif resp.status_code == 400:
        raise RequestNotFoundError(resp.content)
    else:
        raise RequestError(resp.content)
