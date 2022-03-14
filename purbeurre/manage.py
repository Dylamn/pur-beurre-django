#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'purbeurre.settings')
    # len < 2 means no parameter is passed to the script (e.g. "./manage.py")
    running_tests = False if len(sys.argv) < 2 else sys.argv[1] == 'test'

    try:
        if running_tests:
            from coverage import Coverage
            cov = Coverage()
            # Flush the existing coverage.
            cov.erase()
            cov.start()

        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc

    execute_from_command_line(sys.argv)

    if running_tests:
        cov.stop()
        cov.save()


if __name__ == '__main__':
    main()
