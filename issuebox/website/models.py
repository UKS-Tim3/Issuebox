from django.db import models
from django.contrib.auth.models import User, UserManager

class Contributor(User):
    pass

class Issue(models.Model):
    PRIORITIES = (
        ('L', 'Low'),
        ('M', 'Medium'),
        ('H', 'Hi'),        
    )
    STATUSES = (
        (0, 'New'),
        (1, 'In Progress'),
        (2, 'Closed'),
    )

    name = models.CharField(max_length = 50)
    message = models.CharField(max_length = 300)
    created = models.DateTimeField('date published')
    closed = models.DateTimeField('date finished')
    priority = models.CharField(max_length = 1, choices = PRIORITIES)
    status = models.CharField(max_length = 1, choices = STATUSES)

    assignee = models.OneToOneField(
        'Contributor',
        related_name = 'assignee',
        on_delete = models.CASCADE,
    )
    issuer = models.OneToOneField(
        'Contributor',
        related_name = 'issuer',
        on_delete = models.CASCADE,
    )

    def __str__():
        return self.name

class Comment(models.Model):
    message = models.CharField(max_length = 300)
    issue = models.ForeignKey(
        'Issue',
        on_delete = models.CASCADE,
    )
    commenter = models.ForeignKey(
        'Contributor',
        on_delete = models.CASCADE,
    )

    def __str__():
        return self.message

class Tag(models.Model):
    label = models.CharField(max_length = 50)
    color = models.CharField(max_length = 20)
    issue = models.ForeignKey(
        'Issue',
        blank = True,
        related_name = '+',
    )

    def __str__():
        return self.label

class Repository(models.Model):
    name = models.CharField(max_length = 50)

    owner = models.OneToOneField(
        'Contributor',            # temporary solution
    )

class Commit(models.Model):
    message = models.CharField(max_length = 300)

