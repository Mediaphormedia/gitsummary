from social_auth.signals import pre_update, socialauth_registered
from social_auth.backends.contrib.github import GithubBackend
from django.contrib.auth.models import User
from django.db import models
from tastypie.models import create_api_key

try:
    from .models import UserProfile
except ImportError:
    pass


def github_extra_values(sender, user, response, details, **kwargs):
    profile = UserProfile.objects.get_or_create(user=user)[0]
    profile.github_access_token = response.get('access_token')
    profile.save()
    return True

pre_update.connect(github_extra_values, sender=GithubBackend)


def new_users_handler(sender, user, response, details, **kwargs):
    UserProfile.objects.get_or_create(user=user)
    return True

socialauth_registered.connect(new_users_handler, sender=None)
models.signals.post_save.connect(create_api_key, sender=User)
