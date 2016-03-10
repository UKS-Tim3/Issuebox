from django.db import models
from django.contrib.auth.models import User, UserManager

class Contributor(User):
    github_url = models.CharField(max_length = 200)
    img_url = models.CharField(max_length = 200)

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
    contributors = models.ManyToManyField(Contributor)

    owner = models.OneToOneField(
        Contributor,
        related_name = 'owner',
        on_delete = models.CASCADE,
    )

    def __str__(self):
        return self.name

class Commit(models.Model):
    message = models.CharField(max_length = 300)
    contributor = models.ForeignKey(
        Contributor,
        on_delete = models.CASCADE,
    )
    repository = models.ForeignKey(
        Repository,
        on_delete = models.CASCADE,
    )

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
        blank = True,
    )

    assignee = models.ForeignKey(
        Contributor,
        related_name = 'assignee',
        blank = True,
        null = True,
        on_delete = models.CASCADE,
    )
    issuer = models.ForeignKey(
        Contributor,
        related_name = 'issuer',
        on_delete = models.CASCADE,
    )
    commit = models.OneToOneField(
        Commit,
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
        on_delete = models.CASCADE,
    )
    commenter = models.ForeignKey(
        Contributor,
        on_delete = models.CASCADE,
    )

    def __str__(self):
        return self.message

