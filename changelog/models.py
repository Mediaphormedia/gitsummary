from django.conf import settings
from django.db import models
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from timezones.fields import TimeZoneField
from .managers import CommentManager


# Create your models here.
class Org(models.Model):
    user = models.ForeignKey(User, related_name='orgs')
    name = models.CharField(blank=False, max_length=100)

    class Meta:
        unique_together = ('user', 'name')

    def __unicode__(self):
        return self.name


class Repo(models.Model):
    org = models.ForeignKey(Org, related_name='repos')
    name = models.CharField(blank=False, max_length=100)
    url = models.URLField(blank=False)

    class Meta:
        unique_together = ('org', 'name')

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('repo_detail', kwargs={'org_name': self.org.name, 'repo_name': self.name})

    @property
    def settings(self):
        try:
            return self.repo_settings
        except RepoSetting.DoesNotExist:
            return RepoSetting.objects.create(repo=self)


TICKET_NO_REGEX = "#(\d{2,4})"
WORDS = (
    'close',
    'fix',
    'address',
    'ticket',
)
MESSAGES_REGEX = "(%s)" % '|'.join(WORDS)

CHANGELOG_TEMPLATE_DEFAULT = """<% _.each(comments, function(comment) { %><% if (comment.tickets.length) { %><% comment.tickets.each(function(ticket) { %><%= ticket.get('title') %><% }); %>. <% } %><%= comment.get('content') %>

<% }); %>
"""


class RepoSetting(models.Model):
    repo = models.OneToOneField(Repo, related_name='repo_settings')
    ticket_regex = models.CharField(blank=False, max_length=200, default=TICKET_NO_REGEX)
    messages_regex = models.CharField(blank=False, max_length=200, default=MESSAGES_REGEX)
    deploy_regex = models.CharField(blank=False, max_length=200, default='^refs/tags/deploy')
    deploy_datetime_regex = models.CharField(blank=False, max_length=200, default='(\d{4})/(\d{2})/(\d{2})/(\d{2})(\d{2})(\d{2})')
    timezone = TimeZoneField(default=settings.TIME_ZONE)
    changelog_template = models.TextField(blank=False, default=CHANGELOG_TEMPLATE_DEFAULT)

    def __unicode__(self):
        return u"Settings for repo %s" % self.repo.name


TICKET_SOURCE_CHOICES = (
    ('rm', 'redmine'),
    ('gh', 'github'),
)


class Ticket(models.Model):
    source = models.CharField(blank=False, max_length=2, choices=TICKET_SOURCE_CHOICES)
    number = models.PositiveIntegerField()
    title = models.CharField(blank=False, null=False, max_length=255)
    repo = models.ForeignKey(Repo)

    class Meta:
        unique_together = ('source', 'number', 'repo')

    def __unicode__(self):
        return u"%s-%s" % (self.source, self.number)


class Comment(models.Model):
    author = models.ForeignKey(User)
    content = models.TextField(blank=True)
    commit_sha = models.CharField(blank=False, max_length=40, unique=True)
    commit_datetime = models.DateTimeField(blank=False)
    repo = models.ForeignKey(Repo)
    include = models.BooleanField(default=False)
    include_commit_message = models.BooleanField(default=False)
    included_tickets = models.ManyToManyField(Ticket)

    objects = CommentManager()

    def __unicode__(self):
        return u"Comment for %s" % self.commit_sha

    def included_tickets_unicode(self):
        return [u"%s" % ticket for ticket in self.included_tickets.all()]

    def get_ticket_by_unicode(self, ticket_unicode):
        source, number = ticket_unicode.split('-')
        return self.included_tickets.get(source=source, number=int(number))


from .listeners import *
