# Create your views here.
from django.contrib.auth.decorators import login_required
from accounts.models import UserProfile
from django.views.generic import TemplateView


class RepoDetail(TemplateView):
    template_name = 'changelog/repo_detail.html'

    def dispatch(self, request, *args, **kwargs):
        import ipdb; ipdb.set_trace()
        org_name = kwargs['org_name']
        repo_name = kwargs['repo_name']
        tracker = request.user.get_profile().tracker()
        repo = tracker.repos[org_name][repo_name]
        repo.load_refs()
        self.repo = repo

        if 'tag_name' not in kwargs:
            self.selected_deploy = repo.last_deploy()
        else:
            self.selected_deploy = repo.get_deploy(kwargs['tag_name'])

        self.changelog = self.repo.commits(last_tag=self.selected_deploy)

        return super(RepoDetail, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        return super(RepoDetail, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return super(RepoDetail, self).get(request, *args, **kwargs)

    def render_to_response(self, context, **response_kwargs):
        context['object'] = self.repo
        context['selected_deploy'] = self.selected_deploy
        context['changelog'] = self.changelog

        return super(RepoDetail, self).render_to_response(context, **response_kwargs)
