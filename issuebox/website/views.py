from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.core.context_processors import csrf
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponse, HttpResponseRedirect, QueryDict
from django.shortcuts import get_object_or_404, render
from django.template import RequestContext, loader
from django.template.loader import render_to_string
from django.views.generic import DetailView, ListView
from django.views.generic.edit import CreateView, UpdateView
from django.http import JsonResponse
from django.db.models import Q
from django.core.urlresolvers import reverse
import os

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


# We don't user DeleteView because we are not deleting Contributor from database,
# we are just removing it as a contributor from repository
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


# Another way of removing contributor with custom AJAX calls
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


# Issue

class IssueView(DetailView):
    model = Issue
    template_name = 'website/issue/issue.html'


class IssueCreateView(CreateView):
    model = Issue
    form_class = IssueForm
    template_name = 'website/issue/issue_create_form.html'

    # We must override get and form_valid/invalid methods
    # because we need to pass additional data (repository) to templates
    def get(self, request, *args, **kwargs):
        # We must initialize form when overriding get method and pass it in the context
        repository_id = request.GET.get('repo_id')
        repository = get_object_or_404 (Repository, pk=repository_id)
        form = self.form_class(initial=self.initial)
        contibutorsId =[x.id for x in repository.contributors.all()]
        form.fields['assignee'].queryset = Contributor.objects.all().filter(
                                                        Q(pk__in=contibutorsId)|
                                                        Q(pk=repository.owner.pk)
                                            ).distinct();

        template = loader.get_template(self.template_name)
        return HttpResponse(template.render({'repository': repository, 'form': form}, request))

    def form_valid(self, form):
        user = self.request.user

        repository_id = self.request.POST.get('repo_id')
        repository = get_object_or_404 (Repository, pk=repository_id)

        issue = form.save(repository, user)
        return HttpResponse (
            render_to_string ('website/issue/issue_create_success.html', {'issue': issue, 'repository': repository}))

    def form_invalid(self, form):
        # We must extract form from response of super form_invalid method and pass it in the context
        response = super(IssueCreateView, self).form_invalid(form)
        form = response.context_data['form']

        repository_id = self.request.POST.get('repo_id')
        repository = get_object_or_404 (Repository, pk=repository_id)

        template = loader.get_template(self.template_name)
        # we must pass request because we redirect to template with CLRF token (back to form)
        return HttpResponse(template.render({'repository': repository, 'form': form}, self.request))


class IssueEditView (UpdateView):
    model = Issue
    form_class = IssueForm
    template_name = 'website/issue/issue_edit_form.html'

    def get_context_data(self, **kwargs):
        context = super(IssueEditView, self).get_context_data(**kwargs)
        issue_id = self.kwargs['pk']
        issue = get_object_or_404 (Issue, pk=issue_id)
        contibutorsId =[x.id for x in issue.repository.contributors.all()]
        context['form'].fields['assignee'].queryset = Contributor.objects.all().filter(
                                                        Q(pk__in=contibutorsId)|
                                                        Q(pk=issue.repository.owner.pk)
                                            ).distinct();
        return context

    def form_valid(self, form):

        issue = form.save_edit()
        return HttpResponse (
            render_to_string ('website/issue/issue_edit_success.html', {'issue': issue}))

# Tag

class TagListView(ListView):

    template_name = "website/tags/tags.html"
    context_object_name = "tags"
    
    def get_context_data(self, **kwargs):
        context = super(TagListView, self).get_context_data(**kwargs)
        context['default_tags'] = Tag.objects.filter(repository__id = None)

        return context

    def get_queryset(self):
        return Tag.objects.filter(repository__owner=self.request.user) 

class TagDetailView(DetailView):

    model = Tag
    template = "website/tags/tag.html"

class TagCreateView(CreateView):

    model = Tag
    form_class = TagForm
    template_name = 'website/tags/tag_create_form.html'

    def get_form_kwargs(self):
        kwargs = super(TagCreateView, self).get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        repository_id = self.request.POST.get('repository')
        repository = get_object_or_404(Repository, pk=repository_id)

        tag = form.save(repository)

        return HttpResponse (
            render_to_string ('website/tags/tag_create_success.html', {'tag': tag, 'repository': repository}))

class TagEditView(UpdateView):

    model = Tag
    form_class = TagForm
    template_name = 'website/tags/tag_edit_form.html'

    def get_form_kwargs(self):
        kwargs = super(TagEditView, self).get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        repository_id = self.request.POST.get('repository')
        repository = get_object_or_404(Repository, pk=repository_id)

        tag = form.save_edit(repository)
        return HttpResponse (
            render_to_string ('website/tags/tag_edit_success.html', {'tag': tag}))

class TagDeleteView(DetailView):
    model = Tag 
    template_name = 'website/tags/tag_delete_form.html'

    def dispatch(self, *args, **kwargs):
        self.tag_id = kwargs['pk']
        return super (TagDeleteView, self).dispatch (*args, **kwargs)

    def post(self, tag, *args, **kwargs):
        tag = get_object_or_404 (Tag, pk=self.tag_id)
        tag.delete()
        return HttpResponse (
            render_to_string ('website/tags/tag_delete_success.html', {'tag': tag}))



# Commit

class CommitCreateView(CreateView):
    model = Commit
    form_class = CommitForm
    template_name = 'website/commit/commit_create_form.html'

    # We must override get and form_valid/invalid methods
    # because we need to pass additional data (repository) to templates
    def get(self, request, *args, **kwargs):
        # We must initialize form when overriding get method and pass it in the context
        form = self.form_class(initial=self.initial)

        issue_id = request.GET.get('issue_id')
        issue = get_object_or_404 (Issue, pk=issue_id)

        template = loader.get_template(self.template_name)
        return HttpResponse(template.render({'issue': issue, 'form': form}, request))

    def form_valid(self, form):
        user = self.request.user

        issue_id = self.request.POST.get('issue_id')
        issue = get_object_or_404 (Issue, pk=issue_id)

        commit = form.save(issue, user)
        return HttpResponse (
            render_to_string ('website/commit/commit_create_success.html', {'commit': commit, 'issue': issue}))

    def form_invalid(self, form):
        # We must extract form from response of super form_invalid method and pass it in the context
        response = super(CommitCreateView, self).form_invalid(form)
        form = response.context_data['form']

        issue_id = self.request.POST.get('issue_id')
        issue = get_object_or_404 (Issue, pk=issue_id)

        template = loader.get_template(self.template_name)
        # we must pass request because we redirect to template with CLRF token (back to form)
        return HttpResponse(template.render({'issue': issue, 'form': form}, self.request))


class CommitEditView (UpdateView):
    model = Commit
    form_class = CommitForm
    template_name = 'website/commit/commit_edit_form.html'

    def form_valid(self, form):
        user = self.request.user
        commit = form.save_edit(user)
        return HttpResponse (
            render_to_string ('website/commit/commit_edit_success.html', {'commit': commit}))


# Comment

class CommentCreateView(CreateView):
    model = Comment
    form_class = CommentForm
    template_name = 'website/comment/comment_create_form.html'

    # We must override get and form_valid/invalid methods
    # because we need to pass additional data (repository) to templates
    def get(self, request, *args, **kwargs):
        # We must initialize form when overriding get method and pass it in the context
        form = self.form_class(initial=self.initial)

        issue_id = request.GET.get('issue_id')
        issue = get_object_or_404 (Issue, pk=issue_id)

        template = loader.get_template(self.template_name)
        return HttpResponse(template.render({'issue': issue, 'form': form}, request))

    def form_valid(self, form):
        user = self.request.user

        issue_id = self.request.POST.get('issue_id')
        issue = get_object_or_404 (Issue, pk=issue_id)

        comment = form.save(user, issue)
        return HttpResponse (
            render_to_string ('website/comment/comment_create_success.html', {'comment': comment, 'issue': issue}))

    def form_invalid(self, form):
        # We must extract form from response of super form_invalid method and pass it in the context
        response = super(CommentCreateView, self).form_invalid(form)
        form = response.context_data['form']

        issue_id = self.request.POST.get('issue_id')
        issue = get_object_or_404 (Issue, pk=issue_id)

        template = loader.get_template(self.template_name)
        # we must pass request because we redirect to template with CLRF token (back to form)
        return HttpResponse(template.render({'issue': issue, 'form': form}, self.request))


class CommentEditView (UpdateView):
    model = Comment
    form_class = CommentForm
    template_name = 'website/comment/comment_edit_form.html'

    def form_valid(self, form):
        comment = form.save_edit()
        return HttpResponse (
            render_to_string ('website/comment/comment_edit_success.html', {'comment': comment}))


class CommentDeleteView (DetailView):
    model = Comment
    template_name = 'website/comment/comment_delete_form.html'

    def dispatch(self, *args, **kwargs):
        self.comment_id = kwargs['pk']
        return super (CommentDeleteView, self).dispatch (*args, **kwargs)

    def post(self, request, *args, **kwargs):
        comment_id = kwargs['pk']
        comment = get_object_or_404 (Comment, pk=comment_id)
        # comment = get_object_or_404 (Comment, pk=self.comment_id)
        comment.delete ()
        return HttpResponse (
            render_to_string ('website/comment/comment_delete_success.html'))


@login_required
def all_issues(request):
    tags = Tag.objects.all ()

    listOfRepoIds =[]
    contibutorsId =[]
    for repository in request.user.owned_repositories.all():
        listOfRepoIds.append(repository.id)
        for contributor in repository.contributors.all():
            contibutorsId.append(contributor.pk)
        contibutorsId.append(repository.owner.pk)

    for repository in request.user.contributed_repositories.all():
        listOfRepoIds.append(repository.id)
        for contributor in repository.contributors.all():
            contibutorsId.append(contributor.pk)
        contibutorsId.append(repository.owner.pk)

    issues = Issue.objects.all().filter(
        Q(repository__pk__in=listOfRepoIds)
    ).distinct()

    allContributors = Contributor.objects.all().filter(
        Q(pk__in=contibutorsId)
    ).distinct();

    query = request.GET.get ('search_text')
    priority = request.GET.get ('priority')
    status = request.GET.get ('status')
    tag = request.GET.get ('tag')
    repo = request.GET.get ('repo')
    issuerName = request.GET.get ('issuer')
    assigneeName = request.GET.get ('assignee')


    startDateCreated = request.GET.get ('startDateCreated')
    startDateClosed = request.GET.get ('startDateClosed')
    endDateCreated = request.GET.get ('endDateCreated')
    endDateClosed = request.GET.get ('endDateClosed')

    if query:
        issues = issues.filter (Q (name__icontains=query)).distinct ()
    if priority:
        issues = issues.filter (Q (priority__icontains=priority)).distinct ()
    if status:
        issues = issues.filter (Q (status__icontains=status)).distinct ()
    if repo:
        issues = issues.filter (Q (repository__name__icontains=repo)).distinct ()
    if assigneeName:
        if assigneeName =="None":
            listOfUnassigned =[]
            for currentIssue in issues:
                if currentIssue.assignee is None:
                    listOfUnassigned.append(currentIssue.id)

            issues = issues.filter (Q(pk__in=listOfUnassigned)).distinct ()
        else:
            issues = issues.filter (Q (assignee__username__icontains=assigneeName)).distinct ()

    if issuerName:
        issues = issues.filter (Q (issuer__username__icontains=issuerName)).distinct ()

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
        "issuesList": issues,
        "tags": tags,
        "repoCounter": repoCounter,
        "allContributors":allContributors
    }
    template_name = 'website/issue/all_issues.html'
    return render (request, template_name, context)


class ImageURLView(UpdateView):
    model = Contributor
    form_class = ImageURLForm
    template_name = 'website/image/url_form.html'

    # must override this to set object instance in Generic view because <pk> is missing from url
    def get_object(self, queryset=None):
        return self.request.user

    def form_valid(self, form):
        user = self.request.user
        user.img_url = form.save()
        user.save()
        return HttpResponse(
            render_to_string('website/image/image_success.html',
                      {'title': 'Success!',
                       'message': 'Profile image URL has been successfully changed!'}))


def image_upload(request):
    def handle_uploaded_file(file_path, file):
        with open(os.path.join(file_path, file.name), 'wb+') as destination:
            for chunk in file.chunks():
                destination.write(chunk)

    if request.method == 'POST':
        form = ImageUploadForm(request.POST, request.FILES)
        if form.is_valid():
            image = request.FILES['file']
            image_path = os.path.join('website', 'static', 'profile_images')
            if not os.path.exists(image_path):
                os.makedirs(image_path)
            handle_uploaded_file(image_path, image)

            user = request.user
            img_url = os.path.join('profile_images', image.name)
            # double '{{' and '}}' escapes '{}' format field and prints out '{' and '}'
            # user.img_url = '{{% static "{}" %}}'.format(img_url.__str__())
            # but {% static %} tag is not interpreted in template because it is rendered as string
            # in order to avoid changing templates we can hardcode it like this:
            user.img_url = '/static/{}'.format(img_url.__str__())
            user.save()

            return HttpResponse(
                render_to_string('website/image/image_success.html',
                      {'title': 'Success!',
                       'message': 'Profile image has been successfully uploaded!'}))

        else:
            template = loader.get_template('website/image/upload_form.html')
            return HttpResponse(template.render({'form': form}, request))

    elif request.method == 'GET':
        form = ImageUploadForm()
        template = loader.get_template('website/image/upload_form.html')
        return HttpResponse(template.render({'form': form}, request))
