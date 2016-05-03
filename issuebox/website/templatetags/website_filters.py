from django import template

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
