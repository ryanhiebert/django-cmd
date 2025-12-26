import os
import subprocess
import sys
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


@contextmanager
def restore_sys_path():
    """Restore sys.path after the context."""
    saved_path = sys.path.copy()
    yield
    sys.path[:] = saved_path


@restore_environ(["DJANGO_SETTINGS_MODULE"])
def test_configure_from_pyproject_toml_settings_module(tmp_path):
    """Read settings module path from toml file."""
    content = '[tool.django]\nsettings_module = "ball.yarn"\n'
    tmp_path.joinpath("pyproject.toml").write_text(content, encoding="utf-8")
    os.chdir(tmp_path)
    with pytest.warns(DeprecationWarning):
        configure()
    assert os.environ.get("DJANGO_SETTINGS_MODULE") == "ball.yarn"


@restore_environ(["DJANGO_SETTINGS_MODULE"])
def test_configure_from_pyproject_toml(tmp_path):
    """Read settings module path from toml file."""
    content = '[tool.django]\nsettings = "ball.yarn"\n'
    tmp_path.joinpath("pyproject.toml").write_text(content, encoding="utf-8")
    os.chdir(tmp_path)
    configure()
    assert os.environ.get("DJANGO_SETTINGS_MODULE") == "ball.yarn"


@restore_environ(["DJANGO_SETTINGS_MODULE"])
def test_configure_passthru(monkeypatch, tmp_path: Path):
    """It shouldn't change a given DJANGO_SETTINGS_MODULE."""
    monkeypatch.setenv("DJANGO_SETTINGS_MODULE", "spam.eggs")
    content = '[tool.django]\nsettings = "ball.yarn"\n'
    tmp_path.joinpath("pyproject.toml").write_text(content, encoding="utf-8")
    os.chdir(tmp_path)
    configure()
    assert os.environ.get("DJANGO_SETTINGS_MODULE") == "spam.eggs"


@restore_environ(["DJANGO_SETTINGS_MODULE"])
def test_configure_from_pyproject_toml_walktree(tmp_path):
    """Read settings module path from toml file up the tree."""
    content = '[tool.django]\nsettings = "ball.yarn"\n'
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
    with pytest.warns(DeprecationWarning):
        configure()
    assert os.environ.get("DJANGO_SETTINGS_MODULE") == "ball.yarn"


@restore_environ(["DJANGO_SETTINGS_MODULE"])
def test_new_name_from_setup_cfg(tmp_path):
    """Reading the new name from the setup.cfg should give a warning"""
    content = "[django]\nsettings = ball.yarn\n"
    tmp_path.joinpath("setup.cfg").write_text(content, encoding="utf-8")
    os.chdir(tmp_path)
    with pytest.warns(DeprecationWarning):
        configure()
    assert "DJANGO_SETTINGS_MODULE" not in os.environ


@restore_environ(["DJANGO_SETTINGS_MODULE"])
def test_configure_no_configfile(tmp_path):
    """Try to read settings module, but fail and still run command."""
    os.chdir(tmp_path)
    configure()
    assert "DJANGO_SETTINGS_MODULE" not in os.environ


@restore_environ(["DJANGO_SETTINGS_MODULE"])
@restore_sys_path()
def test_configure_adds_path_to_sys_path(tmp_path):
    """Path should be added to sys.path when settings are configured."""
    content = '[tool.django]\nsettings = "ball.yarn"\n'
    tmp_path.joinpath("pyproject.toml").write_text(content, encoding="utf-8")
    os.chdir(tmp_path)
    configure()
    assert str(tmp_path) in sys.path


@restore_environ(["DJANGO_SETTINGS_MODULE"])
@restore_sys_path()
def test_configure_adds_custom_pythonpath(tmp_path):
    """Custom pythonpath should be added to sys.path."""
    subdir = tmp_path.joinpath("src")
    subdir.mkdir()
    content = '[tool.django]\nsettings = "ball.yarn"\npythonpath = "src"\n'
    tmp_path.joinpath("pyproject.toml").write_text(content, encoding="utf-8")
    os.chdir(tmp_path)
    configure()
    assert str(subdir) in sys.path


@restore_environ(["DJANGO_SETTINGS_MODULE"])
@restore_sys_path()
def test_configure_path_without_settings(tmp_path):
    """Path should be added even if settings are not configured."""
    content = '[tool.django]\nsomesetting = "notrelevant"\n'
    tmp_path.joinpath("pyproject.toml").write_text(content, encoding="utf-8")
    os.chdir(tmp_path)
    configure()
    assert str(tmp_path) in sys.path


@restore_environ(["DJANGO_SETTINGS_MODULE"])
def test_check_with_script_target(tmp_path):
    """Should add the pyproject.toml directory to the path."""
    # Run check without a subprocess for coverage.
    from django.core.management import execute_from_command_line

    os.chdir(tmp_path)
    subprocess.run(["django", "startproject", "myproject", "."], check=True)
    config = '[tool.django]\nsettings = "myproject.settings"\n'
    tmp_path.joinpath("pyproject.toml").write_text(config, encoding="utf-8")

    execute_from_command_line(["django", "check"])


@restore_environ(["DJANGO_SETTINGS_MODULE"])
def test_check_with_script_target_subdir(tmp_path):
    """Should add the pyproject.toml directory to the path when in a subdir."""
    # Run check without a subprocess for coverage.
    from django.core.management import execute_from_command_line

    os.chdir(tmp_path)
    subprocess.run(["django", "startproject", "myproject", "."], check=True)
    config = '[tool.django]\nsettings = "myproject.settings"\n'
    tmp_path.joinpath("pyproject.toml").write_text(config, encoding="utf-8")

    subdir = tmp_path.joinpath("subdir")
    subdir.mkdir()
    os.chdir(subdir)

    execute_from_command_line(["django", "check"])


@pytest.mark.parametrize("command", ["django", "django-admin"])
@restore_environ(["DJANGO_SETTINGS_MODULE"])
def test_new_project(command, tmp_path):
    """Should be able to use with a new project."""
    os.chdir(tmp_path)
    subprocess.run([command, "startproject", "myproject", "."], check=True)
    config = '[tool.django]\nsettings = "myproject.settings"\n'
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
    # For reasons I don't understand, this doesn't seem to be cleaning
    # up the port after the test run completes. To kill it, run:
    #
    # lsof -i4:8000 | tail -n 1 | awk '{print $2}' | xargs -n 1 kill -9
    os.chdir(tmp_path)
    subprocess.run([command, "startproject", "myproject", "."], check=True)
    config = '[tool.django]\nsettings = "myproject.settings"\n'
    tmp_path.joinpath("pyproject.toml").write_text(config, encoding="utf-8")
    with pytest.raises(subprocess.TimeoutExpired):
        # Runserver starts a subprocess, but never exits.
        # 1 second is not enough time for it to start and error
        # if the settings module isn't configured correctly.
        # 2 seems to be OK, but to make it hopefully more reliable
        # we'll use 3 seconds. Otherwise this might not break even
        # if the functionality does.
        subprocess.run([command, "runserver"], check=True, timeout=3)
