from .models import *
from django import forms
from django.utils import timezone

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

# User

class RegistrationForm (forms.ModelForm):
    confirmPassword = forms.CharField (widget=forms.PasswordInput (), required=True)
    password = forms.CharField (widget=forms.PasswordInput (), required=True)

    def __init__(self, *args, **kwargs):
        super (RegistrationForm, self).__init__ (*args, **kwargs)

    class Meta:
        model = Contributor
        fields = ['username', 'password', 'confirmPassword', 'first_name', 'last_name', 'email', 'img_url',
                  'github_url']

    def save(self):
        c = Contributor ()
        c.password = password_clean (self.cleaned_data['password'], self.cleaned_data['confirmPassword'])
        c.first_name = self.cleaned_data['first_name']
        c.last_name = self.cleaned_data['last_name']
        c.email = unique_email (self.cleaned_data['email'])
        c.username = self.cleaned_data['username']
        c.img_url = self.cleaned_data['img_url']
        c.github_url = self.cleaned_data['github_url']

        if c.img_url is None or c.img_url=='':
            c.img_url='https://cdn.shopify.com/s/files/1/1069/3046/t/2/assets/noimage.jpg?11257982579509423500'
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
        fields = ['first_name', 'last_name', 'email', 'img_url', 'github_url']

    def save(self, c):
        c.first_name = self.cleaned_data['first_name']
        c.last_name = self.cleaned_data['last_name']
        if c.email != self.cleaned_data['email']:
            c.email = unique_email(self.cleaned_data['email'])
        c.img_url = self.cleaned_data['img_url']
        c.github_url = self.cleaned_data['github_url']

        if c.img_url is None or c.img_url=='':
            c.img_url='https://cdn.shopify.com/s/files/1/1069/3046/t/2/assets/noimage.jpg?11257982579509423500'

        c.save ()
        return c


def unique_email(email):
    if User.objects.filter (email=email).exists ():
        raise forms.ValidationError ("Email already exist.")
    else:
        return email

def password_clean(password, confirmPassword):
    if password != confirmPassword:
        raise forms.ValidationError ("Passwords don't match.")

    return password