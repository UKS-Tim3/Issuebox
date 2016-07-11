from .models import *
from django import forms
from django.utils import timezone
from django.db.models import Q
from itertools import chain
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError
import http.client
from urllib.parse import urlparse

# Repository

class RepositoryForm (forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super (RepositoryForm, self).__init__ (*args, **kwargs)

    class Meta:
        model = Repository
        fields = ['name', 'description', 'github_url']

    def save_create(self, owner):
        repository = Repository()
        repository.name = self.cleaned_data['name']
        repository.description = self.cleaned_data['description']
        repository.github_url = self.cleaned_data['github_url']
        repository.owner = owner
        repository.save()
        return repository

    def save_edit(self):
        repository = self.instance
        repository.name = self.cleaned_data['name']
        repository.description = self.cleaned_data['description']
        repository.github_url = self.cleaned_data['github_url']
        repository.save()
        return repository

class AddContributorForm (forms.ModelForm):
    contributor_id = forms.CharField (widget=forms.HiddenInput(), required=True)

    def __init__(self, *args, **kwargs):
        super (AddContributorForm, self).__init__ (*args, **kwargs)

    class Meta:
        model = Repository
        fields = ['contributor_id']

    def save(self):
        contributor_id = self.cleaned_data['contributor_id']
        return contributor_id


class IssueForm (forms.ModelForm):

    message = forms.CharField(widget=forms.Textarea(attrs={'style':'resize:none', 'rows':'4','placeholder':'Message'}))

    class Meta:
        model = Issue
        fields = ['name', 'message', 'priority', 'status', 'tags', 'assignee']

    def save(self, repository, issuer):
        issue = self.instance
        # using timezone because django throws warning for naive datetime
        issue.created = timezone.now()
        issue.repository = repository
        issue.issuer = issuer
        issue.save()
        return issue

    def save_edit(self):
        issue = self.instance
        contibutorsId =[x.id for x in issue.repository.contributors.all()]
        self.fields['assignee'].queryset = Contributor.objects.all().filter(
                                                        Q(pk__in=contibutorsId)|
                                                        Q(pk=issue.repository.owner.pk)
                                            ).distinct();

        # changing issue status
        if self.initial.get('status') != issue.status:
            # closed
            if issue.status == '2':
                issue.closed = timezone.now()
            # reopened
            else:
                issue.closed = None

        issue.save()
        return issue

# Tag

class TagForm(forms.ModelForm):

    class Meta:
        model = Tag
        fields = ['label', 'font_color', 'background_color'] 

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super (TagForm, self).__init__ (*args, **kwargs)

        repository_id = self.instance.repository.id if self.instance.repository else None

        self.fields['repository'] = forms.ModelChoiceField(
                                                              label = 'Repository',
                                                              initial = repository_id,
                                                              required = False,
                                                              queryset = Repository.objects.all().filter(owner_id = user.id),
                                                          )

    def save(self, repository):
        tag = self.instance
        tag.repository = repository

        tag.save()

        return tag

    def save_edit(self, repository):
        tag = self.instance
        tag.repository = repository

        tag.save()

        return tag

# Commit

class CommitForm(forms.ModelForm):

    class Meta:
        model = Commit
        fields = ['hash', 'message', 'github_url']

    def save(self, issue, user):
        commit = self.instance
        commit.repository = issue.repository
        commit.contributor = user
        commit.save()
        issue.commit = commit
        issue.save()
        return commit

    def save_edit(self, user):
        commit = self.instance
        commit.contributor = user
        commit.save()
        return commit

# Comment

class CommentForm(forms.ModelForm):

    message = forms.CharField(widget=forms.Textarea(attrs={'style':'resize:none', 'rows':'4','placeholder':'Message'}))

    class Meta:
        model = Comment
        fields = ['message']

    def save(self, commenter, issue):
        comment = self.instance
        # using timezone because django throws warning for naive datetime
        comment.timestamp = timezone.now()
        comment.commenter = commenter
        comment.issue = issue
        comment.save()
        return comment

    def save_edit(self):
        comment = self.instance
        comment.save()
        return comment

# User

class RegistrationForm (forms.ModelForm):
    confirmPassword = forms.CharField (widget=forms.PasswordInput (), required=True)
    password = forms.CharField (widget=forms.PasswordInput (), required=True)

    def __init__(self, *args, **kwargs):
        super (RegistrationForm, self).__init__ (*args, **kwargs)

    class Meta:
        model = Contributor
        fields = ['username', 'password', 'confirmPassword', 'first_name', 'last_name', 'email',
                  'github_url']

    def save(self):
        c = Contributor ()
        c.password = password_clean (self.cleaned_data['password'], self.cleaned_data['confirmPassword'])
        c.first_name = self.cleaned_data['first_name']
        c.last_name = self.cleaned_data['last_name']
        c.email = unique_email (self.cleaned_data['email'])
        c.username = self.cleaned_data['username']
        c.github_url = validate_github_url(self.cleaned_data['github_url'])

        c.img_url='/static/assets/noimage.jpg'
        c.save ()

        return c


class ChangePasswordForm (forms.ModelForm):
    oldPassword = forms.CharField (widget=forms.PasswordInput (), required=True)
    newPassword = forms.CharField (widget=forms.PasswordInput (), required=True)
    confirmNewPassword = forms.CharField (widget=forms.PasswordInput (), required=True)

    def __init__(self, *args, **kwargs):
        super (ChangePasswordForm, self).__init__ (*args, **kwargs)

    class Meta:
        model = Contributor
        fields = ['oldPassword', 'newPassword','confirmNewPassword']

    def save(self, c):
        if c.password == self.cleaned_data['oldPassword']:
            c.password = password_clean (self.cleaned_data['newPassword'], self.cleaned_data['confirmNewPassword'])
            c.save()
            return  c
        else:
            raise forms.ValidationError ("Old password doesn't match.")


class RegistrationEditForm (forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super (RegistrationEditForm, self).__init__ (*args, **kwargs)

    class Meta:
        model = Contributor
        fields = ['first_name', 'last_name', 'email', 'github_url']

    def save(self, c):
        c.first_name = self.cleaned_data['first_name']
        c.last_name = self.cleaned_data['last_name']
        if c.email != self.cleaned_data['email']:
            c.email = unique_email(self.cleaned_data['email'])
        c.github_url = validate_github_url(self.cleaned_data['github_url'])

        c.save ()
        return c


def unique_email(email):
    if User.objects.filter (email=email).exists ():
        raise forms.ValidationError ("Email already exist.")
    else:
        return email


def validate_github_url(url):
    # (\s+)?(?!.) means it can have excess of whitespaces
    # only if it is followed by a new line (not followed by any character except new line)
    validate = URLValidator(regex='https?:\/\/(www\.)?github\.com\/\w+(\s+)?(?!.)',
                             message='This seems not to be a valid GitHub url!')
    validate(url)
    return url


def password_clean(password, confirmPassword):
    if password != confirmPassword:
        raise forms.ValidationError ("Passwords don't match.")

    return password


class ImageURLForm(forms.ModelForm):
    class Meta:
        model = Contributor
        fields = ['img_url']

    img_url = forms.CharField(max_length=150, label="Image URL")

    def clean_img_url(self):
        data = self.cleaned_data['img_url']
        if data == '':
            raise forms.ValidationError("This field is required!")
        # elif data[-4:].lower() not in ('.jpg', '.png', '.bmp', '.gif', '.bpg', '.webp'):
        #     raise forms.ValidationError("It seems this is not valid image URL!")

        url = urlparse(data)
        try:
            if not valid_image_url(url, url.scheme == 'https'):
                raise forms.ValidationError("It seems this is not valid image file!")
        except:
            raise forms.ValidationError("There seems to be an error during image url validation!")

        # Always return the cleaned data, whether you have changed it or
        # not.
        return data

    def save(self):
        return self.cleaned_data['img_url']


class ImageUploadForm(forms.Form):

    file = forms.FileField(label='Select an image')

    def clean_file(self):
        data = self.cleaned_data['file']

        if data.name[-4:].lower() not in ('.jpg', '.png', '.bmp', '.gif', '.bpg', '.webp'):
            raise forms.ValidationError("It seems this is not valid image file!")

        # Always return the cleaned data, whether you have changed it or
        # not.
        return data


def valid_image_url(url, secure):
    if secure:
        connection = http.client.HTTPSConnection(url.netloc)
    else:
        connection = http.client.HTTPConnection(url.netloc)

    connection.request("HEAD", url.path)
    response = connection.getresponse()

    # workaround for shortened urls e.g. http://goo.gl/IsSUeBox
    location = response.getheader('Location', None)
    if location is not None and url.__str__() != location:
        location = urlparse(location)
        return valid_image_url(location, location.scheme == 'https')

    if response.code not in range(200, 209):
        return False

    return True if response.getheader('Content-Type', None).startswith('image/') else False
