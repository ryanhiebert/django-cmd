import configparser
import os
import sys
from pathlib import Path

try:
    import tomllib
except ImportError:
    # Python < 3.11
    import tomli as tomllib

from django.core.management import execute_from_command_line


def main():
    """Run Django, getting the default from a file if needed."""
    settings_module = None

    # Load from pyproject.toml first
    pyproject = Path("pyproject.toml")
    if pyproject.is_file():
        with pyproject.open("rb") as f:
            config = tomllib.load(f)
            settings_module = (
                config.get("tool", {}).get("django", {}).get("settings_module")
            )

    if settings_module is None:
        # Try loading configuration from setup.cfg next
        parser = configparser.RawConfigParser()
        parser.read("setup.cfg")
        if parser.has_option("django", "settings_module"):
            settings_module = parser.get("django", "settings_module")

    if settings_module is not None:
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", settings_module)
        if settings_module == os.environ["DJANGO_SETTINGS_MODULE"]:
            sys.path.insert(0, os.getcwd())

    execute_from_command_line(sys.argv)
