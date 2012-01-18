import re
import requests
import simplejson
from dateutil import parser as dateparser

GITHUB_API_URL = 'https://api.github.com'


class RequestError(Exception):
    pass


class RequestNotFoundError(RequestError):
    pass


def find(f, seq):
    """Return first item in sequence where f(item) == True."""
    for item in seq:
        if f(item):
            return item


def request_json(*args, **kwargs):
    resp = requests.get(*args, **kwargs)
    if resp.status_code == 200:
        return simplejson.loads(resp.content)
    elif resp.status_code == 400:
        raise RequestNotFoundError(resp.content)
    else:
        raise RequestError(resp.content)

WORDS = (
    'close',
    'fix',
    'address',
    'ticket',
)
MESSAGES_REGEX = re.compile(r"(%s)" % '|'.join(WORDS), re.IGNORECASE)

TICKET_NO_REGEX = re.compile(r"#(\d{2,4})")

TICKETS_CACHE = {}


class Deploy(object):
    def __init__(self, repo, deploy_dict):
        self.repo = repo
        self.deploy_dict = deploy_dict

    def __eq__(self, other):
        self.deploy_dict['object']['sha'] == other.repo_dict['object']['sha']

    def __getitem__(self, key):
        try:
            return self.deploy_dict[key]
        except KeyError:
            return getattr(self, key)

    @property
    def tag_name(self):
        return self.deploy_dict['ref'].split('refs/tags/')[1]


class Repo(object):
    def __init__(self, tracker, repo_dict, deploys_start_with='deploy'):
        self.tracker = tracker
        self.repo_dict = repo_dict
        self.deploys_start_with = deploys_start_with
        self.refs = []

    def __getitem__(self, key):
        return self.repo_dict[key]

    def _get_tickets(self, message):
        repo_github_api_url = self.repo_dict['url']

        ticket_numbers = set(TICKET_NO_REGEX.findall(message))
        tickets = []
        for n in ticket_numbers:
            ticket = None
            if n in TICKETS_CACHE:
                ticket = TICKETS_CACHE[n]
            else:
                try:
                    ticket = request_json("%s/issues/%s" % (repo_github_api_url, n), headers=self.tracker.GITHUB_AUTH)
                    ticket = {
                        'title': ticket['title'],
                        'url': ticket['html_url'],
                        'number': ticket['number'],
                        'tracker': 'gh',
                    }
                    TICKETS_CACHE['gh-' + n] = ticket
                    tickets.append(ticket)

                except RequestError:
                    pass

                redmine = self.tracker.user.get_profile().redmine
                if redmine is not None:
                    redmine_url = redmine.url
                    redmine_auth = {'X-Redmine-API-Key': redmine.api_key}

                    try:
                        ticket = request_json('%s/issues/%s.json' % (redmine_url, n), headers=redmine_auth)['issue']
                        ticket = {
                            'title': ticket['subject'],
                            'url': '%s/issues/%s' % (redmine_url, n),
                            'number': ticket['id'],
                            'tracker': 'rm',
                        }
                        TICKETS_CACHE['rm-' + n] = ticket
                        tickets.append(ticket)
                    except RequestError:
                        pass

        return tickets

    def org(self):
        return self.tracker.orgs[0]

    def load_refs(self):
        if len(self.refs) == 0:
            repo_github_api_url = self.repo_dict['url']
            refs = request_json('%s/git/refs/tags' % repo_github_api_url, headers=self.tracker.GITHUB_AUTH)
            refs.sort(key=lambda x: x['ref'], reverse=True)
            self.refs = refs
            self.load_deploys()
        return self.refs

    def load_deploys(self):
        if len(self.refs) == 0:
            self.refs = self.load_refs()
        self.deploys = [Deploy(self, ref) for ref in self.refs if ref['ref'].startswith('refs/tags/' + self.deploys_start_with)]
        return self.deploys

    def last_deploy(self):
        return self.deploys[0]

    def get_deploy(self, tag_name):
        if len(self.deploys) == 0:
            self.deploys = self.load_deploys()
        return find(lambda x: x['ref'].endswith(tag_name), self.deploys)

    def commits(self, last_tag=None):
        if len(self.refs) == 0:
            self.refs = self.load_refs()

        repo_github_api_url = self.repo_dict['url']

        if last_tag is None:
            last_tag = self.last_deploy()

        last_tag_name = last_tag['ref'].split('refs/tags/')[1]
        last_tag_sha = last_tag['object']['sha']

        commits_url = '%s/commits' % repo_github_api_url
        commits = request_json(commits_url, data={'sha': last_tag_sha}, headers=self.tracker.GITHUB_AUTH)
        included_commits = [commit for commit in commits if MESSAGES_REGEX.search(commit['commit']['message'])]

        augmented_commits = [
            {
                'commit_object': c,
                'hexsha': c['sha'],
                'message': c['commit']['message'],
                'author': c['commit']['author'],
                'github_url': c['commit']['url'],
                'datetime': dateparser.parse(c['commit']['committer']['date']),
                'tickets': self._get_tickets(c['commit']['message'])
            } for c in included_commits]
        return {
            'last_tag': last_tag_name,
            'commits': augmented_commits
        }


class Tracker(object):
    def __init__(self, user):
        self.user = user
        self.GITHUB_ACCESS_TOKEN = self.user.get_profile().github_access_token
        self.GITHUB_AUTH = {'Authorization': 'token %s' % self.GITHUB_ACCESS_TOKEN}
        self.orgs = self.get_orgs()
        self.repos = self.get_repos()

    def get_orgs(self):
        return request_json('%s/user/orgs' % GITHUB_API_URL, headers=self.GITHUB_AUTH)

    def get_repos(self):
        repos = {
            self.user.username: dict([(r['name'], Repo(self, r)) for r in request_json('%s/user/repos' % GITHUB_API_URL, headers=self.GITHUB_AUTH)])
        }
        for org in self.orgs:
            repos[org['login']] = dict([(r['name'], Repo(self, r)) for r in request_json('%s/repos' % (org['url']), headers=self.GITHUB_AUTH)])

        return repos
