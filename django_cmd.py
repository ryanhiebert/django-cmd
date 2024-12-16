import configparser
import os
import sys

try:
    import tomllib
except ImportError:
    # Python < 3.11
    import tomli as tomllib

from django.core.management import execute_from_command_line


def main():
    """Run Django, getting the default from a file if needed."""
    if "DJANGO_SETTINGS_MODULE" not in os.environ:
        # Try loading configuration from pyproject.toml first
        try:
            with open("pyproject.toml", "rb") as f:
                config = tomllib.load(f)
            settings_module = config["tool"]["django"]["settings_module"]
            os.environ.setdefault("DJANGO_SETTINGS_MODULE", settings_module)
            sys.path.insert(0, "")
        except (FileNotFoundError, KeyError):
            pass  # No pyproject.toml or no settings_module configured

    if "DJANGO_SETTINGS_MODULE" not in os.environ:
        # Try loading configuration from setup.cfg next
        parser = configparser.RawConfigParser()
        parser.read("setup.cfg")
        if parser.has_option("django", "settings_module"):
            settings_module = parser.get("django", "settings_module")
            os.environ.setdefault("DJANGO_SETTINGS_MODULE", settings_module)
            sys.path.insert(0, "")

    execute_from_command_line(sys.argv)
