from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext, loader
from django.views.generic import ListView, DetailView
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .models import *


# Create your views here.
@login_required
def index(request):
    template = loader.get_template ('website/index.html')
    context = RequestContext (request)
    return HttpResponse(template.render (context))


def custom_login(request):
    if request.user.is_authenticated():
        return HttpResponseRedirect('/website/')

    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)

        if user is not None:
            if user.is_active:
                login(request, user)
                return HttpResponseRedirect('/website/')
            else:
                return HttpResponse("Inactive user.")
        return HttpResponseRedirect('/website/login/')

    else:
        template = loader.get_template ('website/login.html')
        context = RequestContext (request)
        return HttpResponse (template.render (context))

@login_required
def custom_logout(request):
    logout(request)
    return HttpResponseRedirect ('/website/login')


@login_required
def tags(request):
    template = loader.get_template ('website/tags.html')
    context = RequestContext (request)
    return HttpResponse (template.render (context))


def registration(request):
    template = loader.get_template ('website/registration.html')
    context = RequestContext (request)
    return HttpResponse (template.render (context))

@login_required
def settings(request, user_id):
    template = loader.get_template ('website/settings.html')
    context = RequestContext (request)
    return HttpResponse (template.render (context), user_id)


class RepositoriesView (ListView):
    model = Repository
    template_name = 'website/all_repositories.html'


class RepositoryDetails (DetailView):
    model = Repository
    template_name = 'website/repository.html'

@login_required
def all_issues(request):
    template = loader.get_template ('website/all_issues.html')
    context = RequestContext (request)
    return HttpResponse (template.render (context))

@login_required
def issue(request):
    template = loader.get_template ('website/issue.html')
    context = RequestContext (request)
    return HttpResponse (template.render (context))
