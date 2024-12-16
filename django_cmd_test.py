import os
import subprocess

from django_cmd import main


def test_main_passthru(monkeypatch, mocker, tmpdir):
    """It shouldn't change a given DJANGO_SETTINGS_MODULE."""
    cmd = mocker.patch("django_cmd.execute_from_command_line")
    monkeypatch.setenv("DJANGO_SETTINGS_MODULE", "spam.eggs")
    content = "[django]\nsettings_module = ball.yarn\n"
    tmpdir.chdir()
    tmpdir.join("setup.cfg").write(content.encode("utf-8"))
    main()
    assert os.environ.get("DJANGO_SETTINGS_MODULE") == "spam.eggs"
    assert cmd.called


def test_main_from_pyproject_toml(mocker, tmpdir):
    """Read settings module path from toml file."""
    cmd = mocker.patch("django_cmd.execute_from_command_line")
    content = '[tool.django]\nsettings_module = "ball.yarn"\n'
    tmpdir.chdir()
    tmpdir.join("pyproject.toml").write(content.encode("utf-8"))
    main()
    assert os.environ.get("DJANGO_SETTINGS_MODULE") == "ball.yarn"
    assert cmd.called
    del os.environ["DJANGO_SETTINGS_MODULE"]


def test_main_from_pyproject_toml_nosetting(mocker, tmpdir):
    """Handle if there's a tool.django section with no settings module."""
    cmd = mocker.patch("django_cmd.execute_from_command_line")
    content = '[tool.django]\nsomesetting = "notrelevant"\n'
    tmpdir.chdir()
    tmpdir.join("pyproject.toml").write(content.encode("utf-8"))
    main()
    assert "DJANGO_SETTINGS_MODULE" not in os.environ
    assert cmd.called


def test_main_from_pyproject_toml_nodjango(mocker, tmpdir):
    """Handle if there's no tool.django section."""
    cmd = mocker.patch("django_cmd.execute_from_command_line")
    content = '[project]\nname = "ball"\n'
    tmpdir.chdir()
    tmpdir.join("pyproject.toml").write(content.encode("utf-8"))
    main()
    assert "DJANGO_SETTINGS_MODULE" not in os.environ
    assert cmd.called


def test_main_from_setup_cfg(mocker, tmpdir):
    """Read settings module path from config file."""
    cmd = mocker.patch("django_cmd.execute_from_command_line")
    content = "[django]\nsettings_module = ball.yarn\n"
    tmpdir.chdir()
    tmpdir.join("setup.cfg").write(content.encode("utf-8"))
    main()
    assert os.environ.get("DJANGO_SETTINGS_MODULE") == "ball.yarn"
    assert cmd.called
    del os.environ["DJANGO_SETTINGS_MODULE"]


def test_main_no_configfile(mocker, tmpdir):
    """Try to read settings module, but fail and still run command."""
    cmd = mocker.patch("django_cmd.execute_from_command_line")
    tmpdir.chdir()
    main()
    assert "DJANGO_SETTINGS_MODULE" not in os.environ
    assert cmd.called


def test_new_project(tmpdir):
    """Should be able to use with a new project."""
    tmpdir.chdir()
    subprocess.run(["django", "startproject", "myproject", "."], check=True)
    config = '[tool.django]\nsettings_module = "myproject.settings"\n'
    tmpdir.join("pyproject.toml").write(config.encode("utf-8"))
    subprocess.run(["django", "check"], check=True)
