from django.db import models
from django.contrib.auth.models import User


# Create your models here.
class Comment(models.Model):
    user = models.ForeignKey(User)
    content = models.TextField(blank=True)
    commit_sha = models.CharField(blank=False, max_length=40, unique=True)
    include = models.BooleanField(default=False)

    def __unicode__(self):
        return u"Comment for %s" % self.commit_sha
