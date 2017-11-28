import os
import sys

try:
    import configparser
except ImportError:  # Python 2
    import ConfigParser as configparser
from django.core.management import execute_from_command_line


def main():
    """Run Django, getting the default from a file if needed."""
    if 'DJANGO_SETTINGS_MODULE' not in os.environ:
        parser = configparser.RawConfigParser()
        parser.read('setup.cfg')
        if parser.has_option('django', 'settings_module'):
            settings_module = parser.get('django', 'settings_module')
            os.environ.setdefault('DJANGO_SETTINGS_MODULE', settings_module)
    execute_from_command_line(sys.argv)
