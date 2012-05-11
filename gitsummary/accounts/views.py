# Create your views here.
from django.views.generic import TemplateView, RedirectView
from django.contrib.auth import logout
from django_git_summary.utils import reverse_lazy
from .forms import SettingsForm


class ProfileDetail(TemplateView):
    template_name = 'accounts/userprofile_detail.html'

    def dispatch(self, request, *args, **kwargs):
        self.userprofile = request.user.get_profile()
        self.settings = self.userprofile.settings
        return super(ProfileDetail, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        self.settings_form = SettingsForm(instance=self.settings)
        return super(ProfileDetail, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.settings_form = SettingsForm(request.POST, instance=self.settings)
        if self.settings_form.is_valid():
            settings = self.settings_form.save(commit=False)
            settings.user = request.user
            settings.save()
        return super(ProfileDetail, self).get(request, *args, **kwargs)

    def render_to_response(self, context, **response_kwargs):
        context['settings_form'] = self.settings_form

        return super(ProfileDetail, self).render_to_response(context, **response_kwargs)


class LogoutView(RedirectView):
    url = reverse_lazy('home')

    def get_redirect_url(self, **kwargs):
        logout(self.request)
        return super(LogoutView, self).get_redirect_url(**kwargs)
