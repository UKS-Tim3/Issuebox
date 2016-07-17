#!/usr/bin/env python
import os
import sys
from getenv import env

from django.core.management import execute_from_command_line

if __name__ == "__main__":
    environment = env('DJANGO_ENV', 'development')

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "issuebox.settings.{}".format(environment))

    execute_from_command_line(sys.argv)
