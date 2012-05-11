from django.db import models
from django.contrib.auth.models import User
from changelog.tracker import Tracker
from changelog.models import Repo


# Create your models here.
class UserSetting(models.Model):
    user = models.OneToOneField(User, related_name='settings')
    redmine = models.BooleanField("look for tickets on Redmine", default=False)
    redmine_url = models.URLField(null=True, unique=True)
    redmine_api_key = models.CharField(null=True, max_length=40)
    github = models.BooleanField("look for tickets on Github", default=False)

    def __unicode__(self):
        return u"settings for %s" % self.user


class UserProfile(models.Model):
    """(UserProfile description)"""
    user = models.ForeignKey(User, unique=True)
    github_access_token = models.CharField(blank=True, null=True, max_length=40)

    def __unicode__(self):
        return u"UserProfile"

    @property
    def settings(self):
        try:
            return self.user.settings
        except UserSetting.DoesNotExist:
            return UserSetting.objects.create(user=self.user)

    def tracker(self):
        gh = Tracker(self.user)
        return gh

    @property
    def repos(self):
        repo_ids = []
        [repo_ids.extend(org.repos.all().values_list('id', flat=True)) for org in self.user.orgs.all()]
        return Repo.objects.filter(id__in=repo_ids)

from .listeners import *
