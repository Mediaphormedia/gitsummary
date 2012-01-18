from django.contrib import admin
from .models import UserProfile, RedmineAccount

admin.site.register(UserProfile)
admin.site.register(RedmineAccount)
