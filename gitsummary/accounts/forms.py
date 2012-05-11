from .models import UserSetting
from django.forms import ModelForm


class SettingsForm(ModelForm):
    class Meta:
        model = UserSetting
        exclude = ('user',)

    def clean(self):
        cleaned_data = self.cleaned_data
        if 'redmine' in cleaned_data and cleaned_data['redmine']:
            msg = u"This field is required."
            if 'redmine_url' not in cleaned_data or cleaned_data['redmine_url'].strip() == u'':
                self._errors["redmine_url"] = self.error_class([msg])
            if 'redmine_api_key' not in cleaned_data or cleaned_data['redmine_api_key'].strip() == u'':
                self._errors["redmine_api_key"] = self.error_class([msg])

        return cleaned_data
