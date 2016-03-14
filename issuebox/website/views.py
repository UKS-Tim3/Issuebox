from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext, loader
from django.views.generic import ListView, DetailView
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from website.auth.backends import have_permission
from django.contrib.auth.decorators import login_required
from .models import *


# Create your views here.

def index(request):
    if request.user.is_authenticated():
        return HttpResponseRedirect('/website/users/'+str(request.user.pk))
    else:
        return HttpResponseRedirect('/website/all-repositories')


def login(request):
    if request.user.is_authenticated():
        return HttpResponseRedirect('/website/')

    template = loader.get_template('website/login.html')
    context = RequestContext(request)

    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)

        if user is not None:
            if user.is_active:
                auth_login(request, user)
                return HttpResponseRedirect('/website/')

        context['username'] = username
        context['error'] = True

    return HttpResponse(template.render(context))


@login_required
def logout(request):
    auth_logout(request)
    return HttpResponseRedirect('/website/login')


@login_required
def tags(request):
    template = loader.get_template('website/tags.html')
    context = RequestContext(request)
    return HttpResponse(template.render(context))


def registration(request):
    if request.user.is_authenticated():
        return HttpResponseRedirect('/website/users/'+str(request.user.pk))
    else:
        template = loader.get_template('website/registration.html')
        context = RequestContext(request)
        return HttpResponse(template.render(context))


@login_required
def settings(request, user_id):
    if have_permission(request.user.pk, user_id):
        template = loader.get_template('website/settings.html')
        context = RequestContext(request)
        return HttpResponse(template.render(context), user_id)
    else:
        return HttpResponseRedirect('/website/users/'+str(request.user.pk))


@login_required
def change_password(request, user_id):
    if have_permission(request.user.pk, user_id):
        template = loader.get_template('website/change_password.html')
        context = RequestContext(request)
        return HttpResponse(template.render(context), user_id)
    else:
        return HttpResponseRedirect('/website/users/'+str(request.user.pk))


class RepositoriesView(ListView):
    model = Repository
    template_name = 'website/all_repositories.html'


class RepositoryDetails(DetailView):
    model = Repository
    template_name = 'website/repository.html'


class ContributorsDetails(DetailView):
    model = Contributor
    template_name = 'website/contributors.html'


#pitanje dal sme/ne sme
@login_required
def all_issues(request):
    template = loader.get_template('website/all_issues.html')
    context = RequestContext(request)
    return HttpResponse(template.render(context))


#pitanje dal sme/ne sme
@login_required
def issue(request):
    template = loader.get_template('website/issue.html')
    context = RequestContext(request)
    return HttpResponse(template.render(context))
