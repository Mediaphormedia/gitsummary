from django.contrib import admin
from .models import Org, Repo, RepoSetting, Comment, Ticket

admin.site.register(Org)
admin.site.register(Repo)
admin.site.register(RepoSetting)
admin.site.register(Comment)
admin.site.register(Ticket)
