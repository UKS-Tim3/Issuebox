from django.db import models
from django.contrib.auth.models import User, UserManager

class Contributor(User):
    github_url = models.CharField(max_length = 200)
    img_url = models.CharField(
        max_length = 200,
        blank = True,
        null = True
    )

    def __str__(self):
        return self.username

class Tag(models.Model):
    label = models.CharField(max_length = 50)
    font_color = models.CharField(
        max_length = 7,
        default = '#000000',
    )
    background_color = models.CharField(
        max_length = 7,
        default = '#FFFFFF',
    )

    def __str__(self):
        return self.label

class Repository(models.Model):
    name = models.CharField(max_length = 50)
    description = models.CharField(
        max_length = 300,
        blank = True,
        null = True,
    )
    github_url = models.CharField(max_length = 200)
    contributors = models.ManyToManyField(
        Contributor,
        related_name = 'contributed_repositories',
    )

    owner = models.ForeignKey(
        Contributor,
        related_name = 'owned_repositories',
        on_delete = models.CASCADE,
    )

    def __str__(self):
        return self.name

class Commit(models.Model):
    hash = models.CharField(max_length = 40)
    message = models.CharField(max_length = 300)
    contributor = models.ForeignKey(
        Contributor,
        related_name = 'commits',
        on_delete = models.CASCADE,
    )
    repository = models.ForeignKey(
        Repository,
        related_name = 'commits',
        on_delete = models.CASCADE,
    )
    github_url = models.CharField(max_length = 200)

    def __str__(self):
        return self.message

class Issue(models.Model):
    PRIORITIES = (
        ('L', 'Low'),
        ('M', 'Medium'),
        ('H', 'High'),        
    )
    STATUSES = (
        ('0', 'New'),
        ('1', 'In Progress'),
        ('2', 'Closed'),
    )

    name = models.CharField(max_length = 50)
    message = models.CharField(
        max_length = 300,
        blank = True,
        null = True,
    )
    created = models.DateTimeField('date published')
    closed = models.DateTimeField(
        'date finished',
        blank = True,
        null = True,
    )
    priority = models.CharField(max_length = 1, choices = PRIORITIES)
    status = models.CharField(max_length = 1, choices = STATUSES)
    tags = models.ManyToManyField(
        Tag,
        related_name='issues',
        blank = True,
    )

    assignee = models.ForeignKey(
        Contributor,
        related_name = 'issues_assigned',
        blank = True,
        null = True,
        on_delete = models.CASCADE,
    )
    issuer = models.ForeignKey(
        Contributor,
        related_name = 'issues_author',
        on_delete = models.CASCADE,
    )
    repository = models.ForeignKey(
        Repository,
        related_name = 'issues',
        on_delete = models.CASCADE,
    )
    commit = models.OneToOneField(
        Commit,
        related_name='issues',
        blank = True,
        null = True,
        on_delete = models.CASCADE,
    )

    def __str__(self):
        return self.name

class Comment(models.Model):
    message = models.CharField(max_length = 300)
    issue = models.ForeignKey(
        Issue,
        related_name = 'comments',
        on_delete = models.CASCADE,
    )
    commenter = models.ForeignKey(
        Contributor,
        related_name = 'comments',
        on_delete = models.CASCADE,
    )
    timestamp = models.DateTimeField('commented on')

    def __str__(self):
        return self.message
