from django import template
import datetime
from django.utils import timezone
from ..models import Comment
from ..models import Issue

register = template.Library()


@register.filter
def is_commited(repository, contributor):
    """Checks if contributor has made commits to the repository."""

    for commit in repository.commits.all():
        if commit.contributor.id == contributor.id:
            return True
    return False

@register.filter
def absolute_url(relative_url):
    """Converts relative url to absolute."""

    url = relative_url
    if not relative_url.startswith('https://'):
        if not relative_url.startswith('http://'):
            url = ''.join(['http://', relative_url])
        else:
            url = ''.join(['https://', relative_url])
    return url

@register.filter
def last_activity(user, repository):
    """Gets user's last activity on this repository."""

    if not user:
        return False

    # 01. 01. 01.
    last_activity = datetime.datetime.fromordinal(1)

    for issue in Issue.objects.filter(issuer=user, repository=repository):
        if issue.created.replace(tzinfo=None) > last_activity:
            last_activity = issue.created.replace(tzinfo=None)
        elif issue.closed.replace(tzinfo=None) > last_activity:
            last_activity = issue.closed.replace(tzinfo=None)
        for comment in Comment.objects.filter(issue=issue, commenter=user):
            if comment.timestamp.replace(tzinfo=None) > last_activity:
                last_activity = comment.timestamp.replace(tzinfo=None)

    return last_activity

@register.filter
def has_last_activity(user, repository):
    """Gets user's last activity on this repository."""

    if not user:
        return False
    # 01. 01. 01.
    last_activity = datetime.datetime.fromordinal(1)

    for issue in Issue.objects.filter(issuer=user, repository=repository):
        if issue.created.replace(tzinfo=None) > last_activity:
            last_activity = issue.created.replace(tzinfo=None)
        elif issue.closed.replace(tzinfo=None) > last_activity:
            last_activity = issue.closed.replace(tzinfo=None)
        for comment in Comment.objects.filter(issue=issue, commenter=user):
            if comment.timestamp.replace(tzinfo=None) > last_activity:
                last_activity = comment.timestamp.replace(tzinfo=None)

    return True if last_activity > datetime.datetime.fromordinal(1) else False
