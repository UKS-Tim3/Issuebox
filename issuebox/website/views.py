from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.core.context_processors import csrf
from django.core.exceptions import ValidationError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.template import RequestContext, loader
from django.template.loader import render_to_string
from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView, UpdateView
from django.http import JsonResponse
from django.db.models import Q

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q

from website.auth.backends import have_permission
from .forms import *
from .forms import RepositoryForm
from .models import *


# Create your views here.

def index(request):
    if request.user.is_authenticated ():
        return HttpResponseRedirect ('/website/users/' + str (request.user.pk))
    else:
        return HttpResponseRedirect ('/website/all-repositories')


def login(request):
    if request.user.is_authenticated ():
        return HttpResponseRedirect ('/website/')

    template = loader.get_template ('website/contributors/login.html')
    context = RequestContext (request)

    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate (username=username, password=password)

        if user is not None:
            if user.is_active:
                auth_login (request, user)
                return HttpResponseRedirect ('/website/')

        context['username'] = username
        context['error'] = True

    return HttpResponse (template.render (context))


@login_required
def logout(request):
    auth_logout (request)
    return HttpResponseRedirect ('/website/login')


@login_required
def tags(request):
    template = loader.get_template ('website/tags.html')
    context = RequestContext (request)
    return HttpResponse (template.render (context))


@login_required
def change_password(request, user_id):
    args = {}
    args.update (csrf (request))
    if have_permission (request.user.pk, user_id):
        if request.method == "POST":
            form = ChangePasswordForm (request.POST)
            try:
                if form.is_valid ():
                    form.save (request.user)
                    user = authenticate (username=request.user.username, password=request.user.password)
                    auth_login (request, user)
                    return HttpResponseRedirect ('/website/users/' + str (request.user.pk))
                else:
                    args['error'] = "Some error ocured."
                    return render (request, 'website/contributors/change_password.html', args)

            except ValidationError as e:
                args['error'] = e.message
                return render (request, 'website/contributors/change_password.html', args)
        else:
            template = loader.get_template ('website/contributors/change_password.html')
            context = RequestContext (request)
            return HttpResponse (template.render (context), user_id)
    else:
        return HttpResponseRedirect ('/website/users/' + str (request.user.pk))


@login_required
def settings(request, user_id):
    args = {}
    args.update (csrf (request))
    if have_permission (request.user.pk, user_id):
        if request.method == "POST":
            form = RegistrationEditForm (request.POST)
            try:
                if form.is_valid ():
                    form.save (request.user)
                    user = authenticate (username=request.user.username, password=request.user.password)
                    auth_login (request, user)
                    return HttpResponseRedirect ('/website/users/' + str (request.user.pk))
                else:
                    args['error'] = "Some error ocured."
                    args['oldVer'] = form
                    return render (request, 'website/contributors/settings.html', args)

            except ValidationError as e:
                args['error'] = e.message
                args['oldVer'] = form
                return render (request, 'website/contributors/settings.html', args)
        else:
            template = loader.get_template ('website/contributors/settings.html')
            context = RequestContext (request)
            context['currentUser'] = request.user
            return HttpResponse (template.render (context), user_id)
    else:
        return HttpResponseRedirect ('/website/users/' + str (request.user.pk))


def registration(request):
    args = {}
    args.update (csrf (request))
    if request.user.is_authenticated ():
        return HttpResponseRedirect ('/website/users/' + str (request.user.pk))
    else:
        if request.method == "POST":
            form = RegistrationForm (request.POST)
            try:
                if form.is_valid ():
                    current_user = form.save ()
                    user = authenticate (username=current_user.username, password=current_user.password)
                    if user is not None:
                        if user.is_active:
                            auth_login (request, user)
                            return HttpResponseRedirect ('/website/')
                else:
                    args['error'] = "Username already exist."
                    args['oldVer'] = form
                    return render (request, 'website/contributors/registration.html', args)

            except ValidationError as e:
                args['error'] = e.message
                args['oldVer'] = form
                return render (request, 'website/contributors/registration.html', args)

    return render (request, 'website/contributors/registration.html', args)



# ------------------
# Repositories
# ------------------
def all_repositories(request):
    repository_list = Repository.objects.all ()

    query = request.GET.get('search_text')
    filterParameter = request.GET.get('filterParameter')

    print(filterParameter)

    if query:
        if filterParameter:
            if filterParameter == "byDescription":
                repository_list = repository_list.filter(description__icontains=query)
            elif filterParameter == "byName":
                repository_list = repository_list.filter(name__icontains=query)
            elif filterParameter == "byOwner":
                repository_list = repository_list.filter(owner__username__icontains=query)
            else:
                repository_list = repository_list.filter(
                    Q(description__icontains=query)|
                    Q(name__icontains=query)|
                    Q(owner__username__icontains=query)
                ).distinct()

    paginator = Paginator(repository_list, 10)
    page = request.GET.get('page')
    try:
        repositories = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        repositories = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        repositories = paginator.page(paginator.num_pages)

    context = {
        "repositories": repositories
    }
    template_name = 'website/repository/all_repositories.html'
    return render(request,template_name, context)


class RepositoryDetails (DetailView):
    model = Repository
    template_name = 'website/repository/repository.html'


class RepositoryCreateView (CreateView):
    model = Repository
    form_class = RepositoryForm
    template_name = 'website/repository/repository_create_form.html'

    def form_valid(self, form):
        repository = form.save ()
        return HttpResponse (
            render_to_string ('website/repository/repository_create_success.html', {'repository': repository}))


class RepositoryEditView (UpdateView):
    model = Repository
    form_class = RepositoryForm
    template_name = 'website/repository/repository_edit_form.html'

    def dispatch(self, *args, **kwargs):
        self.repository_id = kwargs['pk']
        return super (RepositoryEditView, self).dispatch (*args, **kwargs)

    def form_valid(self, form):
        form.save ()
        repository = Repository.objects.get (id=self.repository_id)
        return HttpResponse (
            render_to_string ('website/repository/repository_edit_success.html', {'repository': repository}))


class RepositoryDeleteView (DetailView):
    model = Repository
    template_name = 'website/repository/repository_delete_form.html'

    def dispatch(self, *args, **kwargs):
        self.repository_id = kwargs['pk']
        return super (RepositoryDeleteView, self).dispatch (*args, **kwargs)

    def post(self, request, *args, **kwargs):
        repository = get_object_or_404 (Repository, pk=self.repository_id)
        repository.delete ()
        return HttpResponse (
            render_to_string ('website/repository/repository_delete_success.html', {'repository': repository}))


class AddContributor (UpdateView):
    model = Repository
    form_class = AddContributorForm
    template_name = 'website/repository/repository_add_contributor_form.html'

    def form_valid(self, form):
        form.save ()
        repository = Repository.objects.get (id=self.repository_id)
        return HttpResponse (
            render_to_string ('website/repository/repository_edit_success.html', {'repository': repository}))


def contributor_lookup(request, repository_id):
    print('lookup')
    # Default return list
    results = []
    if request.method == "GET":
        if request.GET.get('query', None):
            query = request.GET['query']
            print('query je {}'.format(query))
            # Ignore queries shorter than length ?
            if len(query) > 0:
                # Q object enables OR operation between filter conditions
                model_results = Contributor.objects.filter(Q(username__icontains=query) |
                        Q(first_name__icontains=query) | Q(last_name__icontains=query) | Q(email__icontains=query))


                # results = [ {x.id : x.username,} for x in model_results ]

                # need to use .all().values() because this converts list of objects which are not Json convertable
                # to list of maps which is literally JSON syntax so JsonResponse can be created
                results = [x for x in model_results.all().values()]
        # else:
        #     # list() and .values([attributes]) must be used in order to serialize to json
        #     results = list(Contributor.objects.all().values())
    return JsonResponse(results, safe=False)


class ContributorsDetails (DetailView):
    model = Contributor
    template_name = 'website/contributors/contributors.html'


# pitanje dal sme/ne sme
@login_required
def all_issues(request):
    template = loader.get_template ('website/all_issues.html')
    context = RequestContext (request)
    return HttpResponse (template.render (context))


# pitanje dal sme/ne sme
@login_required
def issue(request):
    template = loader.get_template ('website/issue.html')
    context = RequestContext (request)
    return HttpResponse (template.render (context))
