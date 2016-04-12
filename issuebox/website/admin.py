from django.contrib import admin

from .models import *

admin.site.register(Contributor)
admin.site.register(Issue)
admin.site.register(Comment)
admin.site.register(Tag)
admin.site.register(Repository)
admin.site.register(Commit)
