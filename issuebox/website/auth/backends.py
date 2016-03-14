from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.hashers import check_password
from website.models import Contributor

class CustomAuthentication(ModelBackend):


    def authenticate(self, username=None, password=None):
         try:
            user = Contributor.objects.get(username=username)

            if user.password == password:
                print("dobra sifra")
                return user
            else:
                # Authentication fails if None is returned
                print("losa sifra")
                return None

         except Contributor.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return Contributor.objects.get(pk=user_id)
        except Contributor.DoesNotExist:
            return None