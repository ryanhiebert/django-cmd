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
