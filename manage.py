#!/usr/bin/env python

from django.core.management import execute_manager

try:
    import settings # Assumed to be in the same directory.
except ImportError:
    print "cannot import settings"

if __name__ == "__main__":
    execute_manager(settings)
