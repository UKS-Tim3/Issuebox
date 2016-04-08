from django import template

register = template.Library()


@register.filter
def is_commited(repository, contributor):
    """Checks if contributor has made commits to the repository."""
    print('called filter for {} and {}'.format(repository.name, contributor.username))
    for commit in repository.commits.all():
        if commit.contributor.id == contributor.id:
            return True
    return False
