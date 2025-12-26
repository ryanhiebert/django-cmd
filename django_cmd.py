import configparser
import os
import sys
from functools import wraps
from pathlib import Path
from warnings import warn

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
    settings = path = None

    # Load from pyproject.toml first
    if pyproject := locate():
        with pyproject.open("rb") as f:
            config = tomllib.load(f)
        settings = config.get("tool", {}).get("django", {}).get("settings")
        if not settings:
            settings = config.get("tool", {}).get("django", {}).get("settings_module")
            if settings:
                warn(
                    "'tool.django.settings_module' in pyproject.toml is deprecated. "
                    "Use 'tool.django.settings' instead.",
                    DeprecationWarning,
                )
        pythonpath = config.get("tool", {}).get("django", {}).get("pythonpath")
        path = pyproject.parent / (pythonpath or ".")

    if settings is None:
        # Try loading configuration from setup.cfg next
        parser = configparser.RawConfigParser()
        parser.read("setup.cfg")
        if parser.has_option("django", "settings_module"):
            settings = parser.get("django", "settings_module")
            path = None if settings is None else Path.cwd()
        if parser.has_section("django"):
            warn(
                "The 'django' section in setup.cfg is deprecated. "
                "Use the 'tool.django' section in pyproject.toml instead.",
                DeprecationWarning,
            )

    if settings is not None:
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", settings)
    if path is not None:
        sys.path.insert(0, str(path))


@wraps(django.core.management.ManagementUtility, updated=())
class ConfiguredManagementUtility(django.core.management.ManagementUtility):
    @wraps(django.core.management.ManagementUtility.execute)
    def execute(self):
        configure()
        return super().execute()


def patch_django():
    django.core.management.ManagementUtility = ConfiguredManagementUtility
