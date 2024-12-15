=================================
django-cmd: Have a django command
=================================

.. image:: https://img.shields.io/pypi/v/django-cmd.svg
   :target: https://pypi.python.org/pypi/django-cmd
   :alt: Latest Version

.. image:: https://github.com/ryanhiebert/django-cmd/actions/workflows/build.yml/badge.svg
   :target: https://github.com/ryanhiebert/django-cmd/actions/workflows/build.yml

.. image:: https://codecov.io/gh/ryanhiebert/django-cmd/graph/badge.svg?token=OK3xJ71rjV
   :target: https://codecov.io/gh/ryanhiebert/django-cmd


Django includes the ``django-admin`` command.
They prefer to not include multiple ways to do the same thing,
but I really want to spell it ``django``.
I also wanted to be able to configure a
default settings module in a configuration file.


Usage
=====

.. code-block:: sh

    pip install django-cmd
    django startproject


Once installed, you can use the ``django`` command
the same as you would normally use the ``django-admin`` command.

Replace manage.py
=================

Did you know that the ``manage.py`` script is just
a thin wrapper around the ``django-admin`` command?
All the wrapper does is set ``DJANGO_SETTINGS_MODULE``
so that it can load your settings and find
any additional commands from your installed apps.
With a tiny bit of configuration,
you can use this ``django`` command in place of ``python manage.py``!

In your ``pyproject.toml`` file,
add a section like this to configure your default settings module:

.. code-block:: toml

    [tool.django]
    settings_module = "myproject.settings"

Or add a section like this to a ``setup.cfg`` file:

.. code-block:: ini

    [django]
    settings_module = myproject.settings

Now you can also use the ``django`` command
everywhere you would normally use ``python manage.py``:

.. code-block:: sh

    django runserver
    django migrate
    django createsuperuser
