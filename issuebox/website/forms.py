from django import forms
from .models import *


class RepositoryForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(RepositoryForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Repository
        fields = ['name', 'description', 'github_url', 'owner', 'contributors']
