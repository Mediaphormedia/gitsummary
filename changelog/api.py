from tastypie import fields
from tastypie.authentication import Authentication
from tastypie.authorization import Authorization
from tastypie.resources import ModelResource
from tastypie.models import ApiKey
from .models import Org, Repo, RepoSetting, Comment, Ticket
from django.contrib.auth.models import User


class ApiKeyAuthentication(Authentication):
    def is_authenticated(self, request, **kwargs):
        token = request.META.get('HTTP_AUTHORIZATION', None)
        if token is None:
            return False

        try:
            key = ApiKey.objects.get(key=token)
        except ApiKey.DoesNotExist:
            return False

        if key.user.is_active:
            request.user = key.user
            return True
        return False


class UserAuthorization(Authorization):
    def is_authorized(self, request, object=None):
        if object is not None:
            return object == request.user
        return False

    def apply_limits(self, request, object_list):
        if request and hasattr(request, 'user'):
            return object_list.filter(id=request.user.id)

        return object_list.none()


class UserResource(ModelResource):
    class Meta:
        queryset = User.objects.all()
        resource_name = 'user'
        authentication = ApiKeyAuthentication()
        authorization = UserAuthorization()


class OrgAuthorization(Authorization):
    def is_authorized(self, request, object=None):
        if object is not None:
            return object.user == request.user
        return True

    def apply_limits(self, request, object_list):
        if request and hasattr(request, 'user'):
            return object_list.filter(user=request.user)

        return object_list.none()


class OrgResource(ModelResource):
    user = fields.ForeignKey(UserResource, 'user')

    class Meta:
        queryset = Org.objects.all()
        resource_name = 'org'
        authentication = ApiKeyAuthentication()
        authorization = OrgAuthorization()

    def alter_deserialized_detail_data(self, request, data):
        if request is not None:
            user_resource_uri = UserResource().get_resource_uri(request.user)
            data['user'] = user_resource_uri

        return super(OrgResource, self).alter_deserialized_detail_data(request, data)


class CommentAuthorization(Authorization):
    user_repos = None

    def _get_user_repos(self, request):
        return request.user.get_profile().repos

    def is_authorized(self, request, object=None):
        if self.user_repos is None:
            self.user_repos = self._get_user_repos(request)

        if object is not None:
            return object.repo in self.user_repos
        return True

    def apply_limits(self, request, object_list):
        if request and hasattr(request, 'user'):
            if self.user_repos is None:
                self.user_repos = self._get_user_repos(request)
            return object_list.filter(repo__in=self.user_repos)

        return object_list.none()


class RepoAuthorization(CommentAuthorization):
    user_orgs = None

    def _get_user_orgs(self, request):
        return request.user.orgs.all()

    def _set_user_orgs(self, request):
        if self.user_orgs is None:
            self.user_orgs = self._get_user_orgs(request)

    def is_authorized(self, request, object=None):
        self._set_user_orgs(request)

        if object is not None:
            return object.org in self.user_orgs
        return True

    def apply_limits(self, request, object_list):
        if request and hasattr(request, 'user'):
            self._set_user_orgs(request)
            return object_list.filter(org__in=self.user_orgs)

        return object_list.none()


class RepoResource(ModelResource):
    org = fields.ForeignKey(OrgResource, 'org')

    class Meta:
        queryset = Repo.objects.all()
        resource_name = 'repo'
        authentication = ApiKeyAuthentication()
        authorization = RepoAuthorization()

    def alter_deserialized_detail_data(self, request, data):
        if request is not None:
            if 'org' not in data and 'org_name' in data:
                org_name = data['org_name']
                org, created = Org.objects.get_or_create(user=request.user, name=org_name)
                org_resource_uri = OrgResource().get_resource_uri(org)
                data['org'] = org_resource_uri

        return super(RepoResource, self).alter_deserialized_detail_data(request, data)


class RepoSettingAuthorization(CommentAuthorization):
    pass


class RepoSettingResource(ModelResource):
    repo = fields.OneToOneField(RepoResource, 'repo')

    class Meta:
        queryset = RepoSetting.objects.all()
        resource_name = 'reposetting'
        authentication = ApiKeyAuthentication()
        authorization = RepoSettingAuthorization()


class TicketAuthorization(CommentAuthorization):
    pass


class TicketResource(ModelResource):
    repo = fields.ForeignKey(RepoResource, 'repo')

    class Meta:
        queryset = Ticket.objects.all()
        resource_name = 'ticket'
        authentication = ApiKeyAuthentication()
        authorization = TicketAuthorization()


class CommentResource(ModelResource):
    author = fields.ForeignKey(UserResource, 'author')
    repo = fields.ForeignKey(RepoResource, 'repo')
    included_tickets = fields.ToManyField(TicketResource, 'included_tickets', related_name='commit')

    class Meta:
        queryset = Comment.objects.all()
        resource_name = 'comment'
        authentication = ApiKeyAuthentication()
        authorization = CommentAuthorization()
