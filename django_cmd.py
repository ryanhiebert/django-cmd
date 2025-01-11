import configparser
import os
import sys
from functools import wraps
from pathlib import Path

try:
    import tomllib
except ImportError:
    # Python < 3.11
    import tomli as tomllib

import django.core.management


def locate() -> Path:
    """Locate the pyproject.toml file."""
    for path in [cwd := Path.cwd(), *cwd.parents]:
        candidate = path / "pyproject.toml"
        if candidate.is_file():
            return candidate


def configure():
    """Run Django, getting the default from a file if needed."""
    settings_module = path = None

    # Load from pyproject.toml first
    if pyproject := locate():
        with pyproject.open("rb") as f:
            config = tomllib.load(f)
        settings_module = (
            config.get("tool", {}).get("django", {}).get("settings_module")
        )
        path = None if settings_module is None else pyproject.parent

    if settings_module is None:
        # Try loading configuration from setup.cfg next
        parser = configparser.RawConfigParser()
        parser.read("setup.cfg")
        if parser.has_option("django", "settings_module"):
            settings_module = parser.get("django", "settings_module")
            path = None if settings_module is None else Path.cwd()

    if settings_module is not None and path is not None:
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", settings_module)
        if settings_module == os.environ["DJANGO_SETTINGS_MODULE"]:
            sys.path.insert(0, str(path))


@wraps(django.core.management.ManagementUtility, updated=())
class ConfiguredManagementUtility(django.core.management.ManagementUtility):
    @wraps(django.core.management.ManagementUtility.execute)
    def execute(self):
        configure()
        return super().execute()


def patch_django():
    django.core.management.ManagementUtility = ConfiguredManagementUtility
