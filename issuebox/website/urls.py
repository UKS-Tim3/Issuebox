from django.conf.urls import patterns, url
from website import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^login/$', views.login, name='login'),
#   DON'T TOUCH, WILL SOON BE INTEGRATED
#   url(r'^tags/$', views.TagsListView.as_view(), name='tags'),
    url(r'^registration/$', views.registration, name='registration'),
    # website/5/setings ?? treba website/user/5/setings
    url(r'^users/(?P<user_id>\d+)/settings/$', views.settings, name='settings'),
    # repositories
    url(r'^logout/$', views.logout, name='logout'),
    url(r'^repositories/(?P<pk>\d+)$', views.RepositoryDetails.as_view(), name='repository'),
    #url(r'^repositories/$', views.RepositoriesView.as_view(), name='all-repositories'),
    url(r'^repositories/create$', views.RepositoryCreateView.as_view(), name='repository_create'),
    url(r'^repositories/(?P<pk>\d+)/edit$', views.RepositoryEditView.as_view(), name='repository_edit'),
    url(r'^repositories/(?P<pk>\d+)/delete$', views.RepositoryDeleteView.as_view(), name='repository_delete'),

    url(r'^registration/$', views.registration, name='registration'),
    url(r'^users/(?P<pk>\d+)$', views.ContributorsDetails.as_view(), name='users'),
    url(r'^users/(?P<user_id>\d+)/settings$', views.settings, name='settings'),
    url(r'^users/(?P<user_id>\d+)/change-password$', views.change_password, name='change-password'),

    url(r'^all-repositories/$', views.all_repositories, name='all-repositories'),

    url(r'^all-issues/$', views.all_issues, name='all-issues'),
    url(r'^issue/$', views.issue, name='issue'),
]
