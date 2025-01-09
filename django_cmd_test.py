import os
import subprocess
from contextlib import contextmanager
from pathlib import Path

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
def test_configure_passthru(monkeypatch, tmp_path: Path):
    """It shouldn't change a given DJANGO_SETTINGS_MODULE."""
    monkeypatch.setenv("DJANGO_SETTINGS_MODULE", "spam.eggs")
    content = "[django]\nsettings_module = ball.yarn\n"
    tmp_path.joinpath("setup.cfg").write_text(content, encoding="utf-8")
    os.chdir(tmp_path)
    configure()
    assert os.environ.get("DJANGO_SETTINGS_MODULE") == "spam.eggs"


@restore_environ(["DJANGO_SETTINGS_MODULE"])
def test_configure_from_pyproject_toml(tmp_path):
    """Read settings module path from toml file."""
    content = '[tool.django]\nsettings_module = "ball.yarn"\n'
    tmp_path.joinpath("pyproject.toml").write_text(content, encoding="utf-8")
    os.chdir(tmp_path)
    configure()
    assert os.environ.get("DJANGO_SETTINGS_MODULE") == "ball.yarn"


@restore_environ(["DJANGO_SETTINGS_MODULE"])
def test_configure_from_pyproject_toml_walktree(tmp_path):
    """Read settings module path from toml file up the tree."""
    content = '[tool.django]\nsettings_module = "ball.yarn"\n'
    tmp_path.joinpath("pyproject.toml").write_text(content, encoding="utf-8")
    subdir = tmp_path.joinpath("subdir")
    subdir.mkdir()
    os.chdir(subdir)
    configure()
    assert os.environ.get("DJANGO_SETTINGS_MODULE") == "ball.yarn"


@restore_environ(["DJANGO_SETTINGS_MODULE"])
def test_configure_from_pyproject_toml_nosetting(mocker, tmp_path):
    """Handle if there's a tool.django section with no settings module."""
    content = '[tool.django]\nsomesetting = "notrelevant"\n'
    tmp_path.joinpath("pyproject.toml").write_text(content, encoding="utf-8")
    os.chdir(tmp_path)
    configure()
    assert "DJANGO_SETTINGS_MODULE" not in os.environ


@restore_environ(["DJANGO_SETTINGS_MODULE"])
def test_main_from_pyproject_toml_nodjango(tmp_path):
    """Handle if there's no tool.django section."""
    content = '[project]\nname = "ball"\n'
    tmp_path.joinpath("pyproject.toml").write_text(content, encoding="utf-8")
    os.chdir(tmp_path)
    configure()
    assert "DJANGO_SETTINGS_MODULE" not in os.environ


@restore_environ(["DJANGO_SETTINGS_MODULE"])
def test_configure_from_setup_cfg(tmp_path):
    """Read settings module path from config file."""
    content = "[django]\nsettings_module = ball.yarn\n"
    tmp_path.joinpath("setup.cfg").write_text(content, encoding="utf-8")
    os.chdir(tmp_path)
    configure()
    assert os.environ.get("DJANGO_SETTINGS_MODULE") == "ball.yarn"


@restore_environ(["DJANGO_SETTINGS_MODULE"])
def test_configure_no_configfile(tmp_path):
    """Try to read settings module, but fail and still run command."""
    os.chdir(tmp_path)
    configure()
    assert "DJANGO_SETTINGS_MODULE" not in os.environ


@restore_environ(["DJANGO_SETTINGS_MODULE"])
def test_check_with_script_target(tmp_path):
    """Run check without a subprocess for coverage."""
    from django.core.management import execute_from_command_line

    os.chdir(tmp_path)
    subprocess.run(["django", "startproject", "myproject", "."], check=True)
    config = '[tool.django]\nsettings_module = "myproject.settings"\n'
    tmp_path.joinpath("pyproject.toml").write_text(config, encoding="utf-8")

    execute_from_command_line(["django", "check"])


@pytest.mark.parametrize("command", ["django", "django-admin"])
@restore_environ(["DJANGO_SETTINGS_MODULE"])
def test_new_project(command, tmp_path):
    """Should be able to use with a new project."""
    os.chdir(tmp_path)
    subprocess.run([command, "startproject", "myproject", "."], check=True)
    config = '[tool.django]\nsettings_module = "myproject.settings"\n'
    tmp_path.joinpath("pyproject.toml").write_text(config, encoding="utf-8")
    os.chdir(tmp_path)
    subprocess.run([command, "check"], check=True)


@pytest.mark.skipif(
    os.environ.get("TOX"),
    reason="Doesn't release the port quickly enough to run multiple times in quick succession with tox.",
)
@pytest.mark.parametrize(
    "command", ["django-admin"]
)  # If django-admin works, so will django
@restore_environ(["DJANGO_SETTINGS_MODULE"])
def test_runserver(command, tmp_path):
    """Should be able to run the development server for several seconds."""
    os.chdir(tmp_path)
    subprocess.run([command, "startproject", "myproject", "."], check=True)
    config = '[tool.django]\nsettings_module = "myproject.settings"\n'
    tmp_path.joinpath("pyproject.toml").write_text(config, encoding="utf-8")
    with pytest.raises(subprocess.TimeoutExpired):
        # Runserver starts a subprocess, but never exits.
        # 1 second is not enough time for it to start and error
        # if the settings module isn't configured correctly.
        # 2 seems to be OK, but to make it hopefully more reliable
        # we'll use 3 seconds. Otherwise this might not break even
        # if the functionality does.
        subprocess.run([command, "runserver"], check=True, timeout=3)
