from django.conf.urls import patterns, url
from website import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^login/$', views.login, name='login'),
    url(r'^tags/$', views.tags, name='tags'),
    url(r'^registration/$', views.registration, name='registration'),
    # website/5/setings ?? treba website/user/5/setings
    url(r'^users/(?P<user_id>\d+)/settings/$', views.settings, name='settings', ),
    # nije ispravan
    url(r'^repository/(?P<pk>\d+)$', views.RepositoryDetails.as_view(), name='repository'),
    url(r'^all-repositories/$', views.RepositoriesView.as_view(), name='all-repositories'),
    url(r'^all-issues/$', views.all_issues, name='all-issues'),
]
