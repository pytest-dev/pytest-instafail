Changelog
---------

Here you can see the full list of changes between each pytest-instafail release.

0.4.2 (June 14, 2020)
^^^^^^^^^^^^^^^^^^^^^

- Fixed usage of deprecated pytest-xdist slave aliases (#20).
- Fixed failing tests on pytest 5

0.4.1 (February 15, 2019)
^^^^^^^^^^^^^^^^^^^^^^^^^

- Fixed compatibility with pytest 4.2.0. Thanks @blueyed for the PR.

0.4.0 (May 19, 2018)
^^^^^^^^^^^^^^^^^^^^

- Added support for Python 3.5, 3.6, and 3.7.
- Dropped support for Python 2.7, 3.2, and 3.3.
- Dropped support for pytest < 2.9.
- Only rewrite lines on tty. Previously you would end up with a \r (^M) in case
  collecting of tests failed, and pytest's output is piped to a file. Thanks
  @blueyed for the PR.
- Support -p no:terminal (#12). Thanks @Maratori for the PR.

0.3.0 (August 30, 2014)
^^^^^^^^^^^^^^^^^^^^^^^

- Added support for Python 3.4
- Added support for pytest 2.6
- Fixed failing tests on pytest 2.6

0.2.0 (March 6, 2014)
^^^^^^^^^^^^^^^^^^^^^

- Dropped support for Python 2.5.
- Fixed stacktrace printed twice when using PDB.
- Fixed internal error when a test marked as xfailing unexpectedly passes
  (David Szotten).

0.1.1 (November 9, 2013)
^^^^^^^^^^^^^^^^^^^^^^^^

- Made pytest-instafail compatible with `pytest-xdist`_'s test parallelization
  (Ronny Pfannschmidt).

0.1.0 (April 8, 2013)
^^^^^^^^^^^^^^^^^^^^^

- Initial public release

.. _`pytest-xdist`: http://pypi.python.org/pypi/pytest-xdist
