from django.db import models


class CommentManager(models.Manager):
    def create_for_commit(self, user, commit, content=''):
        return self.create(**{
            'user': user,
            'commit_sha': commit['sha'],
            'commit_date': commit['datetime'],
            'org_name': commit.repo.org['login'],
            'repo_name': commit.repo['name'],
            'content': content
        })
