from django.conf.urls import patterns, url
from website import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
#   DON'T TOUCH, WILL SOON BE INTEGRATED
#   url(r'^tags/$', views.TagsListView.as_view(), name='tags'),
    # repositories
    url(r'^repositories/(?P<pk>\d+)$', views.RepositoryDetails.as_view(), name='repository'),
    url(r'^repositories/create$', views.RepositoryCreateView.as_view(), name='repository_create'),
    url(r'^repositories/(?P<pk>\d+)/edit$', views.RepositoryEditView.as_view(), name='repository_edit'),
    url(r'^repositories/(?P<pk>\d+)/delete$', views.RepositoryDeleteView.as_view(), name='repository_delete'),
    url(r'^repositories/(?P<pk>\d+)/add_contributor$', views.AddContributorView.as_view(), name='add_contributor'),
    url(r'^repositories/(?P<repository_id>\d+)/contributor_lookup$', views.contributor_lookup, name='contributor_lookup'),
    url(r'^repositories/(?P<repository_id>\d+)/contributor_remove$', views.contributor_remove, name='contributor_remove'),
    url(r'^repositories/(?P<pk>\d+)/contributor_remove/(?P<cid>\d+)$', views.RemoveContributorView.as_view(), name='remove_contributor'),
    url(r'^all-repositories/$', views.all_repositories, name='all-repositories'),

    url(r'^logout/$', views.logout, name='logout'),
    url(r'^login/$', views.login, name='login'),
    url(r'^registration/$', views.registration, name='registration'),

    url(r'^users/(?P<user_id>\d+)$', views.contributors, name='users'),
    url(r'^users/(?P<user_id>\d+)/settings$', views.settings, name='settings'),
    url(r'^users/(?P<user_id>\d+)/change-password$', views.change_password, name='change-password'),
    url(r'^users/(?P<user_id>\d+)/settings/$', views.settings, name='settings'),

    url(r'^all-issues/$', views.all_issues, name='all-issues'),
    url(r'^issues/(?P<pk>\d+)$', views.IssueView.as_view(), name='issue'),
    url(r'^issues/create$', views.IssueCreateView.as_view(), name='issue_create'),
    url(r'^issues/(?P<pk>\d+)/edit$', views.IssueEditView.as_view(), name='issue_edit'),
]
