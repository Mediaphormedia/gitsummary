"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
import os
import codecs
import simplejson
from django.conf import settings
from django.contrib.auth.models import User
from utils import RequestNotFoundError
from changelog.tracker import Repo


class FakeResponse(object):
    def __init__(self, **kwargs):
        self.__dict__ = kwargs


class FakeApiClient(object):
    def __init__(self, user):
        self.user = user

    def fake_request(self, *args, **kwargs):
        url = args[0]
        filepath = os.path.join(settings.PROJ_DIR, 'changelog', 'tests', url.split('//', 1)[1], 'content.json')
        try:
            fh = codecs.open(filepath, 'r', 'utf-8')
            content = fh.read()
            fh.close()
            return FakeResponse(status_code=200, content=content)
        except IOError:
            return FakeResponse(status_code=404)

    def fake_request_json(self, *args, **kwargs):
        url = args[0]
        filepath = os.path.join(settings.PROJ_DIR, 'changelog', 'tests', url.split('//', 1)[1], 'content.json')
        try:
            fh = codecs.open(filepath, 'r', 'utf-8')
            content = fh.read()
        except IOError:
            raise RequestNotFoundError()
        finally:
            fh.close()

        return  simplejson.loads(content)

    def request_json(self, *args, **kwargs):
        return self.fake_request_json(*args, **kwargs)

    def request_head(self, *args, **kwargs):
        return self.fake_request(*args, **kwargs)


class TrackerTest(TestCase):
    fixtures = ['users.json']

    def test_repo(self):
        user = User.objects.get(username='regularuser')
        repo = Repo(user, data_dict={
            'url': self.repo_model.url,
            'name': repo_name,
            'org_name': org_name
        })
        repo.api_client = FakeApiClient(user)
