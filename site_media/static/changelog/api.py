from tastypie.authentication import Authentication
from tastypie.authorization import Authorization
from tastypie.resources import ModelResource
from tastypie.models import ApiKey
from .models import Comment


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


class CommentAuthorization(Authorization):
    def is_authorized(self, request, object=None):
        if object is not None:
            return object.user == request.user
        return True

    def apply_limits(self, request, object_list):
        if request and hasattr(request, 'user'):
            return object_list.filter(user__username=request.user.username)

        return object_list.none()


class CommentResource(ModelResource):
    class Meta:
        queryset = Comment.objects.all()
        resource_name = 'comment'
        authentication = ApiKeyAuthentication()
        authorization = CommentAuthorization()
