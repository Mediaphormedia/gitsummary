from django.contrib import admin
from .models import UserProfile, UserSetting

admin.site.register(UserProfile)
admin.site.register(UserSetting)
