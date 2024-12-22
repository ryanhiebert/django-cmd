import os
import subprocess
from contextlib import contextmanager

import pytest

from django_cmd import configure


@contextmanager
def restore_environ(keys):
    """Restore the given environment keys after the context."""
    missing = {key for key in keys if key not in os.environ}
    saved = {key: os.environ[key] for key in keys if key in os.environ}
    yield
    for key in missing:
        if key in os.environ:
            del os.environ[key]
    for key, value in saved.items():
        os.environ[key] = value


@restore_environ(["DJANGO_SETTINGS_MODULE"])
def test_configure_passthru(monkeypatch, tmpdir):
    """It shouldn't change a given DJANGO_SETTINGS_MODULE."""
    monkeypatch.setenv("DJANGO_SETTINGS_MODULE", "spam.eggs")
    content = "[django]\nsettings_module = ball.yarn\n"
    tmpdir.chdir()
    tmpdir.join("setup.cfg").write(content.encode("utf-8"))
    configure()
    assert os.environ.get("DJANGO_SETTINGS_MODULE") == "spam.eggs"


@restore_environ(["DJANGO_SETTINGS_MODULE"])
def test_configure_from_pyproject_toml(tmpdir):
    """Read settings module path from toml file."""
    content = '[tool.django]\nsettings_module = "ball.yarn"\n'
    tmpdir.chdir()
    tmpdir.join("pyproject.toml").write(content.encode("utf-8"))
    configure()
    assert os.environ.get("DJANGO_SETTINGS_MODULE") == "ball.yarn"


@restore_environ(["DJANGO_SETTINGS_MODULE"])
def test_configure_from_pyproject_toml_nosetting(mocker, tmpdir):
    """Handle if there's a tool.django section with no settings module."""
    content = '[tool.django]\nsomesetting = "notrelevant"\n'
    tmpdir.chdir()
    tmpdir.join("pyproject.toml").write(content.encode("utf-8"))
    configure()
    assert "DJANGO_SETTINGS_MODULE" not in os.environ


@restore_environ(["DJANGO_SETTINGS_MODULE"])
def test_main_from_pyproject_toml_nodjango(tmpdir):
    """Handle if there's no tool.django section."""
    content = '[project]\nname = "ball"\n'
    tmpdir.chdir()
    tmpdir.join("pyproject.toml").write(content.encode("utf-8"))
    configure()
    assert "DJANGO_SETTINGS_MODULE" not in os.environ


@restore_environ(["DJANGO_SETTINGS_MODULE"])
def test_configure_from_setup_cfg(tmpdir):
    """Read settings module path from config file."""
    content = "[django]\nsettings_module = ball.yarn\n"
    tmpdir.chdir()
    tmpdir.join("setup.cfg").write(content.encode("utf-8"))
    configure()
    assert os.environ.get("DJANGO_SETTINGS_MODULE") == "ball.yarn"


@restore_environ(["DJANGO_SETTINGS_MODULE"])
def test_configure_no_configfile(tmpdir):
    """Try to read settings module, but fail and still run command."""
    tmpdir.chdir()
    configure()
    assert "DJANGO_SETTINGS_MODULE" not in os.environ


@restore_environ(["DJANGO_SETTINGS_MODULE"])
def test_check_with_script_target(tmpdir):
    """Run check without a subprocess for coverage."""
    from django.core.management import execute_from_command_line

    tmpdir.chdir()
    subprocess.run(["django", "startproject", "myproject", "."], check=True)
    config = '[tool.django]\nsettings_module = "myproject.settings"\n'
    tmpdir.join("pyproject.toml").write(config.encode("utf-8"))

    execute_from_command_line(["django", "check"])


@pytest.mark.parametrize("command", ["django", "django-admin"])
@restore_environ(["DJANGO_SETTINGS_MODULE"])
def test_new_project(command, tmpdir):
    """Should be able to use with a new project."""
    tmpdir.chdir()
    subprocess.run([command, "startproject", "myproject", "."], check=True)
    config = '[tool.django]\nsettings_module = "myproject.settings"\n'
    tmpdir.join("pyproject.toml").write(config.encode("utf-8"))
    subprocess.run([command, "check"], check=True)


@pytest.mark.skipif(
    os.environ.get("TOX"),
    reason="Doesn't release the port quickly enough to run multiple times in quick succession with tox.",
)
@pytest.mark.parametrize(
    "command", ["django-admin"]
)  # If django-admin works, so will django
@restore_environ(["DJANGO_SETTINGS_MODULE"])
def test_runserver(command, tmpdir):
    """Should be able to run the development server for several seconds."""
    tmpdir.chdir()
    subprocess.run([command, "startproject", "myproject", "."], check=True)
    config = '[tool.django]\nsettings_module = "myproject.settings"\n'
    tmpdir.join("pyproject.toml").write(config.encode("utf-8"))
    with pytest.raises(subprocess.TimeoutExpired):
        # Runserver starts a subprocess, but never exits.
        # 1 second is not enough time for it to start and error
        # if the settings module isn't configured correctly.
        # 2 seems to be OK, but to make it hopefully more reliable
        # we'll use 3 seconds. Otherwise this might not break even
        # if the functionality does.
        subprocess.run([command, "runserver"], check=True, timeout=3)
