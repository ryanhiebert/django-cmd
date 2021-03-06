import os
import subprocess
from django_cmd import main


def test_main_passthru(monkeypatch, mocker, tmpdir):
    """It shouldn't change a given DJANGO_SETTINGS_MODULE."""
    cmd = mocker.patch('django_cmd.execute_from_command_line')
    monkeypatch.setenv('DJANGO_SETTINGS_MODULE', 'spam.eggs')
    content = u'[django]\nsettings_module = ball.yarn\n'
    tmpdir.chdir()
    tmpdir.join('setup.cfg').write(content.encode('utf-8'))
    main()
    assert os.environ.get('DJANGO_SETTINGS_MODULE') == 'spam.eggs'
    assert cmd.called


def test_main_from_configfile(monkeypatch, mocker, tmpdir):
    """Read settings module path from config file."""
    cmd = mocker.patch('django_cmd.execute_from_command_line')
    content = u'[django]\nsettings_module = ball.yarn\n'
    tmpdir.chdir()
    tmpdir.join('setup.cfg').write(content.encode('utf-8'))
    main()
    assert os.environ.get('DJANGO_SETTINGS_MODULE') == 'ball.yarn'
    assert cmd.called
    del os.environ['DJANGO_SETTINGS_MODULE']


def test_main_no_configfile(monkeypatch, mocker, tmpdir):
    """Try to read settings module, but fail and still run command."""
    cmd = mocker.patch('django_cmd.execute_from_command_line')
    print(tmpdir)
    tmpdir.chdir()
    main()
    assert 'DJANGO_SETTINGS_MODULE' not in os.environ
    assert cmd.called


def test_call_command():
    """Should have installed a "django" command."""
    subprocess.call(['django'])
