from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import ensure_csrf_cookie
from django.core.context_processors import csrf
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponse, HttpResponseRedirect, QueryDict
from django.shortcuts import get_object_or_404, render
from django.template import RequestContext, loader
from django.template.loader import render_to_string
from django.views.generic import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.http import JsonResponse
from django.db.models import Q

from website.auth.backends import have_permission
from .forms import *
from .forms import RepositoryForm, IssueForm
from .models import *
from datetime import datetime


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

    query = request.GET.get ('search_text')
    filterParameter = request.GET.get ('filterParameter')
    if filterParameter is None:
        filterParameter = 'all'

    if query:
        if filterParameter == "byDescription":
            repository_list = repository_list.filter (description__icontains=query)
        elif filterParameter == "byName":
            repository_list = repository_list.filter (name__icontains=query)
        elif filterParameter == "byOwner":
            repository_list = repository_list.filter (owner__username__icontains=query)
        else:
            repository_list = repository_list.filter (
                Q (description__icontains=query) |
                Q (name__icontains=query) |
                Q (owner__username__icontains=query)
            ).distinct ()

    paginator = Paginator (repository_list, 10)
    page = request.GET.get ('page')
    try:
        repositories = paginator.page (page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        repositories = paginator.page (1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        repositories = paginator.page (paginator.num_pages)

    context = {
        "repositories": repositories
    }
    template_name = 'website/repository/all_repositories.html'
    return render (request, template_name, context)


class RepositoryDetails (DetailView):
    model = Repository
    template_name = 'website/repository/repository.html'

    # ensures that csrf cookie is set to response view
    # @method_decorator(ensure_csrf_cookie)
    def dispatch(self, *args, **kwargs):
        return super(RepositoryDetails, self).dispatch(*args, **kwargs)


class RepositoryCreateView (CreateView):
    model = Repository
    form_class = RepositoryForm
    template_name = 'website/repository/repository_create_form.html'

    def form_valid(self, form):
        user = self.request.user
        repository = form.save_create(user)
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
        repository = form.save_edit()
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


class AddContributorView (UpdateView):
    model = Repository
    form_class = AddContributorForm
    template_name = 'website/repository/repository_add_contributor_form.html'

    def dispatch(self, *args, **kwargs):
        self.repository_id = kwargs['pk']
        return super(AddContributorView, self).dispatch(*args, **kwargs)

    def form_valid(self, form):
        contributor_id = form.save()

        repository = get_object_or_404(Repository, pk=self.repository_id)
        contributor = get_object_or_404(Contributor, pk=contributor_id)

        # if not already a contributor
        if contributor.id not in [x.id for x in repository.contributors.all()]:
            repository.contributors.add(contributor)
            return HttpResponse(
            render_to_string('website/repository/repository_add_contributor_success.html',
                              {'repository': repository, 'contributor': contributor}))

        else:
            return HttpResponse(
                render_to_string('website/repository/repository_add_contributor_error.html',
                                  {'repository': repository, 'contributor': contributor}))


def contributor_lookup(request, repository_id):
    # Default return list
    results = []
    if request.method == "GET":
        if request.GET.get('query', None):
            query = request.GET['query']
            # Ignore queries shorter than length ?
            if len(query) > 0:
                # Q object enables OR operation between filter conditions
                model_results = Contributor.objects.filter(Q(username__icontains=query) |
                        Q(first_name__icontains=query) | Q(last_name__icontains=query) | Q(email__icontains=query))

                # results = [ {x.id : x.username,} for x in model_results ]

                # need to use .all().values() because this converts query set of objects which are not Json convertable
                # to list of maps which is literally JSON syntax so JsonResponse can be created
                results = [x for x in model_results.all().values()]

                # removing repository owner and user that are already contributors
                repository = get_object_or_404 (Repository, pk=repository_id)
                results = [x for x in results if x['id'] not in [y.id for y in repository.contributors.all()]
                                                    and x['id'] != repository.owner.id]

        # else:
        #     # list() and .values([attributes]) must be used in order to serialize to json
        #     results = list(Contributor.objects.all().values())
    return JsonResponse(results, safe=False)


class RemoveContributorView (DetailView):
    model = Repository
    template_name = 'website/repository/repository_remove_contributor_form.html'

    def get(self, request, *args, **kwargs):
        pk = kwargs['pk']
        cid = kwargs['cid']
        repository = get_object_or_404 (Repository, pk=pk)
        contributor = get_object_or_404 (Contributor, pk=cid)

        # Because target template has form with CSRF token, we must pass the request context to it.
        # When using this and passing context to the response via render_to_string method
        # template engine has problems with handling RequestContext object
        # context = RequestContext(request)
        # context.update({'repository': repository, 'contributor': contributor})

        # instead, use this (this handles CSRF token successfuly)
        template = loader.get_template(self.template_name)
        return HttpResponse(template.render({'repository': repository, 'contributor': contributor}, request))

    def post(self, request, *args, **kwargs):
        pk = kwargs['pk']
        cid = kwargs['cid']
        repository = get_object_or_404 (Repository, pk=pk)
        contributor = get_object_or_404 (Contributor, pk=cid)

        # if is a contributor
        if contributor.id in [x.id for x in repository.contributors.all()]:
            repository.contributors.remove(contributor)
            return HttpResponse(
                render_to_string('website/repository/repository_remove_contributor_success.html',
                          {'repository': repository, 'contributor': contributor}))

        else:
            return HttpResponse(
                render_to_string('website/repository/repository_remove_contributor_error.html',
                                  {'repository': repository, 'contributor': contributor}))


def contributor_remove(request, repository_id):
    if request.method == "DELETE":

        # Unless GET or POST requests, QueryDict must be used to retrieve request data
        delete = QueryDict(request.body)

        cid = delete.get('contributor_id', None)
        if cid is not None:
            repository = get_object_or_404 (Repository, pk=repository_id)
            contributor = get_object_or_404 (Contributor, pk=cid)

            # if is a contributor
            if contributor.id in [x.id for x in repository.contributors.all()]:
                repository.contributors.remove(contributor)
                return HttpResponse(
                    render_to_string('website/repository/repository_remove_contributor_success.html',
                              {'repository': repository, 'contributor': contributor}))

            else:
                return HttpResponse(
                    render_to_string('website/repository/repository_remove_contributor_error.html',
                                      {'repository': repository, 'contributor': contributor}))

    return HttpResponse(
            render_to_string('website/framework/generic_message.html',
                      {'title': 'Error!',
                       'message': 'Sorry! An error occured while removing contributor!'}))


def contributors(request, user_id):
    user = Contributor.objects.get (pk=user_id)
    context = {
        "userPage": user
    }

    template_name = 'website/contributors/contributors.html'
    return render (request, template_name, context)


class IssueView(DetailView):
    model = Issue
    template_name = 'website/issue.html'


class CreateIssueView(CreateView):
    model = Issue
    form_class = IssueForm
    template_name = 'website/issue/issue_create_form.html'

    # Overriding methods because we need to pass additional data (repository) to templates
    # Arguments must be caught in dispatch method because it precedes every other method
    # and they use our arguments
    def dispatch(self, *args, **kwargs):
        self.repository_id = kwargs['pk']
        return super(CreateIssueView, self).dispatch(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        repository = get_object_or_404 (Repository, pk=self.repository_id)

        # We must initialize form when overriding get method and pass it in the context
        form = self.form_class(initial=self.initial)

        template = loader.get_template(self.template_name)
        return HttpResponse(template.render({'repository': repository, 'form': form}, request))

    def form_invalid(self, form):
        # We must extract form from response of super form_invalid method and pass it in the context
        response = super(CreateIssueView, self).form_invalid(form)
        form = response.context_data['form']

        repository = get_object_or_404 (Repository, pk=self.repository_id)

        template = loader.get_template(self.template_name)
        return HttpResponse(template.render({'repository': repository, 'form': form}, response._request))

    def form_valid(self, form):
        user = self.request.user
        repository = get_object_or_404 (Repository, pk=self.repository_id)
        issue = form.save(repository, user)
        return HttpResponse (
            render_to_string ('website/issue/issue_create_success.html', {'issue': issue, 'repository': repository}))


@login_required
def all_issues(request):
    tags = Tag.objects.all ()
    issues = Issue.objects.all ().filter (
        Q (assignee__username__exact=request.user.username) |
        Q (issuer__username__exact=request.user.username)
    ).distinct ()

    query = request.GET.get ('search_text') if request.GET.get ('search_text') else ''
    priority = request.GET.get ('priority') if request.GET.get ('priority') else ''
    status = request.GET.get ('status') if request.GET.get ('status') else ''
    tag = request.GET.get ('tag')
    repo = request.GET.get ('repo') if request.GET.get ('repo') else ''

    startDateCreated = request.GET.get ('startDateCreated') if request.GET.get ('startDateCreated') else ''
    startDateClosed = request.GET.get ('startDateClosed') if request.GET.get ('startDateClosed') else ''
    endDateCreated = request.GET.get ('endDateCreated') if request.GET.get ('endDateCreated') else ''
    endDateClosed = request.GET.get ('endDateClosed') if request.GET.get ('endDateClosed') else ''

    issues = issues.filter (
        Q (priority__icontains=priority) &
        Q (status__icontains=status) &
        # Q(repo__name__exact=repo)&
        Q (name__icontains=query)
    ).distinct ()

    if tag:
        issues = issues.filter (Q (tags__label__icontains=tag)).distinct ()
    if startDateCreated:
        try:
            issues = issues.filter (Q (created__gte=datetime.strptime (startDateCreated, '%Y-%m-%d'))).distinct ()
        except:
            pass
    if startDateClosed:
        try:
            issues = issues.filter (Q (created__gte=datetime.strptime (startDateClosed, '%Y-%m-%d'))).distinct ()
        except:
            pass
    if endDateCreated:
        try:
            issues = issues.filter (Q (created__lte=datetime.strptime (endDateCreated, '%Y-%m-%d'))).distinct ()
        except:
            pass
    if endDateClosed:
        try:
            issues = issues.filter (Q (created__lte=datetime.strptime (endDateClosed, '%Y-%m-%d'))).distinct ()
        except:
            pass


    paginator = Paginator (issues, 10)
    page = request.GET.get ('page')
    try:
        issues = paginator.page (page)
    except PageNotAnInteger:
        issues = paginator.page (1)
    except EmptyPage:
        issues = paginator.page (paginator.num_pages)

    repoCounter = len (request.user.owned_repositories.all ()) + len (request.user.contributed_repositories.all ())
    context = {
        "issues": issues,
        "tags": tags,
        "repoCounter": repoCounter
    }
    template_name = 'website/all_issues.html'
    return render (request, template_name, context)


# pitanje dal sme/ne sme
@login_required
def issue(request):
    template = loader.get_template ('website/issue.html')
    context = RequestContext (request)
    return HttpResponse (template.render (context))
