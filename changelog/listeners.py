from django.db import models

try:
    from .models import Repo, RepoSetting
except ImportError:
    pass


def create_repo_setting(sender, instance, created, **kwargs):
    if created:
        RepoSetting.objects.get_or_create(repo=instance)

models.signals.post_save.connect(create_repo_setting, sender=Repo)
