from django.db import models
from django.contrib.auth.models import User
from changelog.tracker import Tracker
from django.core.cache import cache


# Create your models here.
class RedmineAccount(models.Model):
    user = models.ForeignKey(User, unique=True, related_name='redmine_accounts')
    url = models.URLField(blank=False, unique=True)
    api_key = models.CharField(blank=False, max_length=40)

    def __unicode__(self):
        return u"redmine account for %s" % self.user


class UserProfile(models.Model):
    """(UserProfile description)"""
    user = models.ForeignKey(User, unique=True)
    github_access_token = models.CharField(blank=True, null=True, max_length=40)

    def __unicode__(self):
        return u"UserProfile"

    @property
    def redmine(self):
        redmine_accounts = self.user.redmine_accounts.all()
        if len(redmine_accounts) > 0:
            return self.user.redmine_accounts.all()[0]
        return None

    def tracker(self):
        gh = cache.get('tracker:%s' % self.user.username)
        if gh is None:
            gh = Tracker(self.user)
            cache.set('tracker:%s' % self.user.username, gh, 60 * 5)
        return gh

from .listeners import *
