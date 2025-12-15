2.7 (2025-01-11)
++++++++++++++++

* Add support for Python 3.14, Django 5.2, and Django 6.0.

2.6 (2025-01-10)
++++++++++++++++

* Use the ``pyproject.toml`` directory as the path
  when discovered by walking up the tree.

2.5 (2025-01-09)
++++++++++++++++

* Remove accidentally added debug print.
* Add ruff linting and print checking.

2.4 (2025-01-09)
++++++++++++++++

* Walk up the tree to find ``pyproject.toml``.

2.3 (2024-12-20)
++++++++++++++++

* Support configuration when using
  the built-in ``django-admin`` command.

2.2 (2024-12-19)
++++++++++++++++

* Add the directory to the Python path
  if the settings module from the configuration file
  is the same as it is in the environment.
  This allows ``django runserver`` to work.

2.1 (2024-12-16)
++++++++++++++++

* Automatically add the directory to the Python path
  when a configuration file is found.

2.0 (2024-12-15)
++++++++++++++++

* Require Python >= 3.8
* Require Django >= 2.0
* Read configuration from pyproject.toml
