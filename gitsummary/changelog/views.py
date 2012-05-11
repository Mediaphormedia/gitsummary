# Create your views here.
from .models import Comment, Repo
from .tracker import Repo as RepoTracker
from .tracker import Org
from django.views.generic import TemplateView
from .forms import SettingsForm


class RepoDetail(TemplateView):
    template_name = 'changelog/repo_detail.html'

    def dispatch(self, request, *args, **kwargs):
        org_name = kwargs['org_name']
        repo_name = kwargs['repo_name']

        self.repo_model = Repo.objects.get(name=repo_name, org__name=org_name)
        self.repo = RepoTracker(request.user, data_dict={
            'url': self.repo_model.url,
            'name': repo_name,
            'org_name': org_name
        })

        self.repo.load_refs()

        if 'tag_name' not in kwargs:
            self.selected_deploy = self.repo.last_deploy()
        else:
            self.selected_deploy = self.repo.get_deploy(kwargs['tag_name'])

        self.changelog = self.repo.commits(last_tag=self.selected_deploy)

        shas = [commit_container['commit'].sha for commit_container in self.changelog['commits']]
        self.comments = Comment.objects.filter(commit_sha__in=shas)
        return super(RepoDetail, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        return super(RepoDetail, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return super(RepoDetail, self).get(request, *args, **kwargs)

    def render_to_response(self, context, **response_kwargs):
        context['object'] = self.repo
        context['object_model'] = self.repo_model
        context['selected_deploy'] = self.selected_deploy
        context['changelog'] = self.changelog
        context['comments'] = self.comments
        return super(RepoDetail, self).render_to_response(context, **response_kwargs)


class RepoSettingsView(TemplateView):
    template_name = 'changelog/repo_settings.html'

    def dispatch(self, request, *args, **kwargs):
        org_name = kwargs['org_name']
        repo_name = kwargs['repo_name']

        self.repo_model = Repo.objects.get(name=repo_name, org__name=org_name)

        self.userprofile = request.user.get_profile()
        self.settings = self.repo_model.settings
        return super(RepoSettingsView, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        self.settings_form = SettingsForm(instance=self.settings)
        return super(RepoSettingsView, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.settings_form = SettingsForm(request.POST, instance=self.settings)
        if self.settings_form.is_valid():
            settings = self.settings_form.save(commit=False)
            settings.repo = self.repo_model
            settings.save()
        return super(RepoSettingsView, self).get(request, *args, **kwargs)

    def render_to_response(self, context, **response_kwargs):
        context['settings_form'] = self.settings_form
        context['object'] = self.repo_model

        return super(RepoSettingsView, self).render_to_response(context, **response_kwargs)
