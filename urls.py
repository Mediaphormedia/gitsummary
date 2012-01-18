from django.conf.urls.defaults import patterns, include, url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf import settings
# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()
from django.views.generic.simple import direct_to_template, redirect_to

from accounts.views import ProfileDetail, LogoutView
from changelog.views import RepoDetail, RepoSettingsView
from django.contrib.auth.decorators import login_required

from tastypie.api import Api
from changelog.api import CommentResource, OrgResource, RepoResource, RepoSettingResource, UserResource, TicketResource


v1_api = Api(api_name='v1')
v1_api.register(CommentResource())
v1_api.register(OrgResource())
v1_api.register(RepoResource())
v1_api.register(RepoSettingResource())
v1_api.register(TicketResource())
v1_api.register(UserResource())

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'django_git_summary.views.home', name='home'),
    # url(r'^django_git_summary/', include('django_git_summary.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
    url(r'', include('social_auth.urls')),
    url(r'^repos/(?P<org_name>[-\w]+)/(?P<repo_name>[-\w]+)/changelog/(?P<tag_name>[-\w\/]+)$', login_required(RepoDetail.as_view()), name='repo_detail_tag'),
    url(r'^repos/(?P<org_name>[-\w]+)/(?P<repo_name>[-\w]+)/changelog/$', login_required(RepoDetail.as_view()), name='repo_detail'),
    url(r'^repos/(?P<org_name>[-\w]+)/(?P<repo_name>[-\w]+)/settings/$', login_required(RepoSettingsView.as_view()), name='repo_settings'),
    url(r'^repos/manage/$', login_required(direct_to_template), {'template': 'changelog/repo_manage.html'}, name="repo_manage"),
    url(r'^accounts/logout/$', LogoutView.as_view(), name='accounts_logout'),
    url(r'^accounts/login/$', redirect_to, {'url': '/'}, name='accounts_login'),
    url(r'^accounts/profile/$', login_required(ProfileDetail.as_view()), name='userprofile_detail'),
    url(r'^api/', include(v1_api.urls)),
    url(r'^$', direct_to_template, {'template': 'index.html'}, name="home"),
)

urlpatterns += staticfiles_urlpatterns()
