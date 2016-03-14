from django.contrib.auth.backends import ModelBackend
from website.models import Contributor


class CustomAuthentication (ModelBackend):
    def authenticate(self, username=None, password=None):
        try:
            user = Contributor.objects.get (username=username)

            if user.password == password:
                return user
            else:
                # Authentication fails if None is returned
                return None

        except Contributor.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return Contributor.objects.get (pk=user_id)
        except Contributor.DoesNotExist:
            return None


def have_permission(authenticated_user_id, user_id):
    if str(authenticated_user_id) == user_id:
        return True
    else:
        return False
