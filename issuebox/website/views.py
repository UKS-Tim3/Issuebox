from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django.template import RequestContext, loader
from django.views.generic import ListView, DetailView
from django.views.generic.edit import UpdateView
from django.template.loader import render_to_string
from .models import *
from .forms import RepositoryForm


# Create your views here.
# @login_required
def index(request):
    template = loader.get_template('website/index.html')
    context = RequestContext(request)
    return HttpResponse(template.render(context))

def login(request):
    template = loader.get_template('website/login.html')
    context = RequestContext(request)
    return HttpResponse(template.render(context))


def tags(request):
    template = loader.get_template('website/tags.html')
    context = RequestContext(request)
    return HttpResponse(template.render(context))


def registration(request):
    template = loader.get_template('website/registration.html')
    context = RequestContext(request)
    return HttpResponse(template.render(context))


def settings(request, user_id):
    template = loader.get_template('website/settings.html')
    context = RequestContext(request)
    return HttpResponse(template.render(context), user_id)

def all_issues(request):
    template = loader.get_template('website/all_issues.html')
    context = RequestContext(request)
    return HttpResponse(template.render(context))

def issue(request):
    template = loader.get_template('website/issue.html')
    context = RequestContext(request)
    return HttpResponse(template.render(context))


# ------------------
# Repositories
# ------------------
class RepositoriesView(ListView):
    model = Repository
    template_name = 'website/repository/all_repositories.html'


class RepositoryDetails(DetailView):
    model = Repository
    template_name = 'website/repository/repository.html'


class RepositoryEditView(UpdateView):
    model = Repository
    form_class = RepositoryForm
    template_name = 'website/repository/repository_edit_form.html'

    def dispatch(self, *args, **kwargs):
        self.repository_id = kwargs['pk']
        return super(RepositoryEditView, self).dispatch(*args, **kwargs)

    def form_valid(self, form):
        form.save()
        repository = Repository.objects.get(id=self.repository_id)
        return HttpResponse(render_to_string('website/repository/repository_edit_form_success.html', {'repository': repository}))


class RepositoryDeleteView(DetailView):
    model = Repository
    template_name = 'website/repository/repository_delete_view.html'

    def dispatch(self, *args, **kwargs):
        self.repository_id = kwargs['pk']
        return super(RepositoryDeleteView, self).dispatch(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        repository = get_object_or_404(Repository, pk=self.repository_id)
        repository.delete()
        return HttpResponse(render_to_string('website/repository/repository_delete_success.html', {'repository': repository}))
