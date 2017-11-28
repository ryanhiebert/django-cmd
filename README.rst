================================
django-cmd: Get a django command
================================

.. image:: https://img.shields.io/pypi/v/django-cmd.svg
   :target: https://pypi.python.org/pypi/django-cmd
   :alt: Latest Version

.. image:: https://travis-ci.org/ryanhiebert/django-cmd.svg?branch=master
   :target: https://travis-ci.org/ryanhiebert/django-cmd

.. image:: https://codecov.io/gh/ryanhiebert/django-cmd/branch/master/graph/badge.svg
   :target: https://codecov.io/gh/ryanhiebert/django-cmd


Django only includes the ``django-admin``.
They prefer to not include multiple ways to do the same thing,
but I really want to spell it ``django``.
I also wanted to be able to configure a
default settings file in a ``setup.cfg`` configuration file.


Usage
=====

.. code-block:: sh

    pip install django-cmd
    django startproject


Once installed, you can use the ``django`` command
the same as you would normally use the ``django-admin`` command.
Additionally, you can add a section like this to a ``setup.cfg`` file
to configure the ``DJANGO_SETTINGS_MODULE``
that you would like to use when no other is specified.

.. code-block:: ini

    [django]
    settings_module = myproject.settings

That's it! Have fun!
