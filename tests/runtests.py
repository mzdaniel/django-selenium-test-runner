#!/usr/bin/env python
"""Test django-selenium-test-runner"""

import sys, os
import settings
from django.core.management import setup_environ, call_command

if __name__ == "__main__":
    # Allow tests to run even without package installation.
    saved_working_directory = os.getcwd()
    os.chdir(os.path.realpath(os.path.dirname(__file__)))
    sys.path = ['..'] + sys.path

    setup_environ(settings)
    failures = call_command('test', verbosity=9)
    # Restore original directory
    os.chdir(saved_working_directory)
    if failures:
        sys.exit(failures)
