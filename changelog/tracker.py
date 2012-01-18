import re
import requests
import logging
from django.core.cache import cache
from datetime import datetime
from dateutil import parser as dateparser
from utils import request_json, find, RequestError
from .models import RepoSetting
from .models import Ticket as TicketModel


logger = logging.getLogger('django_git_summary.debug')

GITHUB_API_URL = 'https://api.github.com'


class ApiClient(object):
    def __init__(self, user):
        self.user = user
        self.GITHUB_ACCESS_TOKEN = self.user.get_profile().github_access_token
        self.GITHUB_AUTH = {'Authorization': 'token %s' % self.GITHUB_ACCESS_TOKEN}

    def request_json(self, *args, **kwargs):
        kwargs['headers'] = self.GITHUB_AUTH
        return request_json(*args, **kwargs)

    def request_head(self, *args, **kwargs):
        kwargs['headers'] = self.GITHUB_AUTH
        return requests.head(*args, **kwargs)


class GitHubObject(object):
    def __init__(self, user):
        self.user = user
        self.api_client = ApiClient(self.user)


class DictObject(GitHubObject):
    def __init__(self, user, data_dict):
        super(DictObject, self).__init__(user)
        self.data_dict = data_dict

    def __getattr__(self, name):
        if name in self.data_dict:
            return self.data_dict[name]
        raise AttributeError


class Ticket(DictObject):
    _model = False

    @property
    def source(self):
        return self.tracker

    @property
    def model(self):
        if self._model is False:
            try:
                self._model = TicketModel.objects.get(source=self.source, number=self.number)
            except Ticket.DoesNotExist:
                self._model = None
        return self._model


class Commit(DictObject):
    def __init__(self, user, data_dict, repo):
        self.repo = repo
        super(Commit, self).__init__(user, data_dict)

    def __eq__(self, other):
        self.data_dict['object']['sha'] == other.data_dict['object']['sha']

    @property
    def commit(self):
        return self.data_dict['commit']

    @property
    def datetime(self):
        return dateparser.parse(self.commit['committer']['date'])

    @property
    def message(self):
        return self.commit['message']

    @property
    def author(self):
        return self.data_dict['commit']['author']

    @property
    def github_url(self):
        try:
            org_name = self.repo.org_name
        except AttributeError:
            org_name = self.repo.org.name
        return u"https://github.com/%s/%s/commit/%s" % (org_name, self.repo.name, self.sha)


class Deploy(Commit):
    def __init__(self, user, data_dict, repo):
        self._commit = None
        self._datetime = None
        super(Deploy, self).__init__(user, data_dict, repo)

    @property
    def commit(self):
        if self._commit is None:
            self._commit = self.api_client.request_json(self.data_dict['object']['url'])
        return self._commit

    @property
    def tag_name(self):
        return self.data_dict['ref'].split('refs/tags/')[1]

    @property
    def datetime(self):
        if self._datetime is None:
            datetime_tuple = map(int, self.repo.deploy_datetime_regex.findall(self.tag_name)[0])
            self._datetime = datetime(*datetime_tuple, tzinfo=self.repo.prefs.timezone)
        return self._datetime

    @property
    def github_url(self):
        return self.data_dict['url']

    @property
    def message(self):
        return None


class RepoDefaultPrefs(object):
    def __getattr__(self, name):
        try:
            return RepoSetting._meta.get_field_by_name(name)[0].default
        except:
            raise AttributeError


class Repo(GitHubObject):
    def __init__(self, user, data_dict, org=None, deploys_start_with='deploy'):
        super(Repo, self).__init__(user)
        self.org = org
        self.data_dict = data_dict
        try:
            self.prefs = RepoSetting.objects.get(repo__name=self.name)
        except RepoSetting.DoesNotExist:
            self.prefs = RepoDefaultPrefs()
        self.deploy_datetime_regex = re.compile(self.prefs.deploy_datetime_regex)
        #self.deploys_start_with = deploys_start_with
        self.refs = []

    def __getattr__(self, name):
        if name in self.data_dict:
            return self.data_dict[name]
        raise AttributeError

    def _get_tickets(self, message):
        repo_github_api_url = self.data_dict['url']
        ticket_regex = re.compile(self.prefs.ticket_regex)

        ticket_numbers = set(ticket_regex.findall(message))
        tickets = []
        settings = self.user.get_profile().settings

        cache_time = 60 * 5
        for n in ticket_numbers:
            if settings.github:
                cache_key = 'ticket:gh-%s:data_dict' % n
                data_dict = cache.get(cache_key)
                if data_dict is None:
                    try:
                        data_dict = self.api_client.request_json("%s/issues/%s" % (repo_github_api_url, n))
                    except RequestError:
                        pass
                if data_dict is not None:
                    ticket = Ticket(self.user, data_dict={
                        'title': data_dict['title'],
                        'url': data_dict['html_url'],
                        'number': data_dict['number'],
                        'tracker': 'gh',
                        'unicode': 'gh-%d' % data_dict['number'],
                    })
                    cache.set(cache_key, data_dict, cache_time)
                    tickets.append(ticket)

            if settings.redmine:
                cache_key = 'ticket:rm-%s:data_dict' % n
                data_dict = cache.get(cache_key)

                redmine_url = settings.redmine_url

                if data_dict is None:
                    redmine_auth = {'X-Redmine-API-Key': settings.redmine_api_key}

                    try:
                        data_dict = request_json('%s/issues/%s.json' % (redmine_url, n), headers=redmine_auth)['issue']

                    except RequestError:
                        pass

                if data_dict is not None:
                    ticket = Ticket(self.user, data_dict={
                        'title': data_dict['subject'],
                        'url': '%s/issues/%s' % (redmine_url, n),
                        'number': data_dict['id'],
                        'tracker': 'rm',
                        'unicode': 'rm-%d' % data_dict['id'],
                    })
                    cache.set(cache_key, data_dict, cache_time)
                    tickets.append(ticket)

        return tickets

    def load_refs(self):
        if len(self.refs) == 0:
            repo_github_api_url = self.data_dict['url']
            refs = self.api_client.request_json('%s/git/refs/tags' % repo_github_api_url)
            self.refs = refs
            self.load_deploys()
        return self.refs

    def load_deploys(self):
        deploy_regex = re.compile(self.prefs.deploy_regex)
        if len(self.refs) == 0:
            self.refs = self.load_refs()
        self.deploys = [Deploy(self.user, ref, self) for ref in self.refs if deploy_regex.search(ref['ref'])]
        self.deploys.sort(key=lambda x: x.datetime, reverse=True)
        return self.deploys

    def last_deploy(self):
        return self.deploys[0]

    def get_deploy(self, tag_name):
        if len(self.deploys) == 0:
            self.deploys = self.load_deploys()
        return find(lambda x: x.ref.endswith(tag_name), self.deploys)

    def commits(self, last_tag=None):
        if len(self.refs) == 0:
            self.refs = self.load_refs()

        repo_github_api_url = self.data_dict['url']

        if last_tag is None:
            last_tag = self.last_deploy()

        last_tag_name = last_tag.ref.split('refs/tags/')[1]

        commits_url = '%s/commits' % repo_github_api_url
        commits = self.api_client.request_json(commits_url)
        messages_regex = re.compile(self.prefs.messages_regex)
        included_commits = [commit for commit in commits if dateparser.parse(commit['commit']['author']['date']) > last_tag.datetime and messages_regex.search(commit['commit']['message'])]

        augmented_commits = [
            {
                'commit': Commit(self.user, c, self),
                'tickets': self._get_tickets(c['commit']['message'])
            } for c in included_commits]
        return {
            'last_tag': last_tag_name,
            'commits': augmented_commits
        }


class Personal(GitHubObject):
    def __init__(self, user, tracker=None):
        super(Personal, self).__init__(user)
        self.tracker = tracker
        self.repos = self.get_repos()

    @property
    def url(self):
        return '%s/user' % GITHUB_API_URL

    @property
    def name(self):
        return self.user.username

    def _repo_has_tags(self, repo_dict):
        resp = self.api_client.request_head('%s/git/refs/tags' % repo_dict['url'])
        logger.debug("%s - %s" % (resp.status_code, resp.url))
        return resp.status_code != 404

    def get_candidates(self):
        url = '%s/repos' % self.url
        return self.api_client.request_json(url)

    def get_repos(self):

        repos = dict([(r['name'], Repo(self.user, r, self)) for r in self.get_candidates() if self._repo_has_tags(r)])
        return repos


class Org(Personal):
    def __init__(self, user, data_dict, tracker=None):
        self.data_dict = data_dict
        super(Org, self).__init__(user, tracker)

    def __getattr__(self, name):
        if name in self.data_dict:
            return self.data_dict[name]
        raise AttributeError

    @property
    def url(self):
        return self.data_dict['url']

    @property
    def name(self):
        return self.data_dict['login']

    def get_repos(self):
        repos = dict([(r['name'], Repo(self.user, r, self)) for r in self.get_candidates() if not r['fork'] and self._repo_has_tags(r)])
        return repos


class Tracker(GitHubObject):
    def __init__(self, user):
        super(Tracker, self).__init__(user)
        self.orgs = self.get_orgs()

    def get_orgs(self):
        orgs = [Personal(self.user, self)]
        orgs += [Org(self.user, org_dict, self) for org_dict in self.api_client.request_json('%s/user/orgs' % GITHUB_API_URL, headers=self.api_client.GITHUB_AUTH)]
        return orgs

    @property
    def repos(self):
        repos = []
        [repos.extend(org.repos) for org in self.orgs]
        return repos
