from .models import RepoSetting
from django.forms import ModelForm


class SettingsForm(ModelForm):
    class Meta:
        model = RepoSetting
        exclude = ('repo',)
