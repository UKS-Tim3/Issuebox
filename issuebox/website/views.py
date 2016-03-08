from django.shortcuts import render
from django.http import HttpResponse
from django.template import RequestContext, loader
from django.views.generic import ListView, DetailView
from .models import *


# Create your views here.
#@login_required
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


def settings(request,user_id):
    template = loader.get_template('website/settings.html')
    context = RequestContext(request)
    return HttpResponse(template.render(context),user_id)

class RepositoriesView(ListView):
    model = Repository
    template_name = 'website/all_repositories.html'

class RepositoryDetails(DetailView):
    model = Repository
    template_name = 'website/repository.html'
