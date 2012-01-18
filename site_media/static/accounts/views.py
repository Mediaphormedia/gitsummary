# Create your views here.
from django.views.generic import TemplateView, RedirectView
from django.views.generic.base import TemplateResponseMixin
from django.views.generic.edit import FormView
from django.contrib.auth import logout
from django_git_summary.utils import reverse_lazy
from .forms import RedmineAccountForm


class ProfileDetail(TemplateView):
    template_name = 'accounts/userprofile_detail.html'

    def dispatch(self, request, *args, **kwargs):
        self.userprofile = request.user.get_profile()
        return super(ProfileDetail, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        redmine = self.userprofile.redmine
        self.redmine_form = RedmineAccountForm(instance=redmine)
        return super(ProfileDetail, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        redmine = self.userprofile.redmine
        self.redmine_form = RedmineAccountForm(request.POST, instance=redmine)
        if self.redmine_form.is_valid():
            redmine = self.redmine_form.save(commit=False)
            redmine.user = request.user
            redmine.save()
        return super(ProfileDetail, self).get(request, *args, **kwargs)

    def render_to_response(self, context, **response_kwargs):
        context['redmine_form'] = self.redmine_form

        return super(ProfileDetail, self).render_to_response(context, **response_kwargs)


class LogoutView(RedirectView):
    url = reverse_lazy('home')

    def get_redirect_url(self, **kwargs):
        logout(self.request)
        return super(LogoutView, self).get_redirect_url(**kwargs)
