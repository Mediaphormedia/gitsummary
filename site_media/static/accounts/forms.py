from .models import RedmineAccount
from django.forms import ModelForm


class RedmineAccountForm(ModelForm):
    class Meta:
        model = RedmineAccount
        exclude = ('user',)
