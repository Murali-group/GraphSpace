#!/usr/bin/env python
import os
import sys
import subprocess

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "graphspace.settings.production")

    from django.core.management import execute_from_command_line
    execute_from_command_line(sys.argv)