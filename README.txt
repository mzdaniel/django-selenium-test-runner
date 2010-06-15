###########################
django-selenium-test-runner
###########################

`django-selenium-test-runner`_ incorporates functional testing into Django's
manage.py test subcommand using `Selenium web testing tools`_.


Background
==========

This package was made to facilitate and simplify functional testing in Django
using Selenium tools.

Selenium tests are code that emulate a user/web browser interaction allowing
automatic web server testing. These tests can be created using `selenium-ide`_
and exported as python files for this test runner to use them. Selenium-ide
allows to record in real time a user interaction with a web browser, in a
similar way as a macro recorder in word processing applications.

`Fixtures`_ are fixed data fed into the database at the beginning of each
test run. The idea is that each test run against a consistent predefined state.
Fixtures can be created using manage.py dumpdata [options] [appname ...]


Installation
============

If you have `setuptools`_ installed, you can simply run the following command::

    sudo easy_install django-selenium-test-runner

If you downloaded the package, you can just unpack it with::

    tar zxvf django-selenium-test-runner-0.1.0.tar.gz

and copy "dstest" directory tree to Python's site-packages directory, which is
usually located at:

    /usr/lib/python2.4/site-packages (Unix, Python 2.4)
    /usr/lib/python2.5/site-packages (Unix, Python 2.5)
    /usr/lib/python2.6/dist-packages (Unix, Python 2.6)

django-selenium-test-runner is enabled in the project's settings.py with::

    TEST_RUNNER = 'dstest.test_runner.run_tests'


Usage
=====

Both, django unittest and selenium tests will be run with the standard command::

  python manage.py test [options] [appname ...]

The exported selenium tests will be searched in django_app_dir/tests/selenium/
directories where django_app_dir is an application defined in INSTALLED_APPS.
This default can be changed with the setting SELENIUM_TESTS_PATH. Test names
start with "test_". As these tests will be imported, please be sure to create
django_app_dir/tests/__init__.py and django_app_dir/tests/selenium/__init__.py
files as any python package.

Fixture data is loaded by default from django_app_dir/fixtures/tests/data.json
at the beginning of each selenium test. This default can be change using the
FIXTURES setting.


Settings
========

There is only one required setting into your project's settings.py, assuming
django-selenium-test-runner is correctly installed:

TEST_RUNNER = 'dstest.test_runner.run_tests'

optional settings are:

* SELENIUM_TESTS_PATH - Changes default directories to look for Selenium tests
    within the application directories. (Default: 'tests/selenium')

* FIXTURES - List of fixture files to load within the django_app_dir/fixtures
    directories. (Default: ['tests/data.json'])

* SELENIUM_PATH - Directory path for Selenium RC jar its python driver
   (i.e.: selenium-server.jar and selenium.py)
   (Default: path where django-selenium-test-runner/dstest is installed)


Testing the package
===================

django-selenium-test-runner comes with its own test suite based on the Django
`tutorial`_. It is designed to serve as example in a Django admin application,
and showcase django-selenium-test-runner capabilities. To run it, cd into the
tests directory of the package and execute::

    python runtests


Dependencies
============

Most dependencies are integrated in the django-selenium-test-runner package.
For now, either Sqlite 3 or Postgres is required as more testing is needed to
make it database agnostic.

Included in django-selenium-test-runner package:

* `Selenium RC server and python driver`_. Provide selenium testing engine.
    Tested with selenium-server.jar and selenium.py v1.0.1

* `CherryPy WSGI multi-thread web server`_. Provide a reliable web server.
    Tested with wsgiserver.py v3.1.2

* `Django mediahandler.py`_, by Artem Egorkine. Provide static media handler.

Not included in the package:

* `Python 2.x`_ where x >= 4. Tested with Python v2.6

* `Django 1.x`_. Tested with Django v1.1

* `Java VM command line runner`_. Provide selenium-server.jar dependency.
    Tested with java openjdk-6-jre.

* `Sqlite 3`. Provided by Python v2.5 or higher.

* `Postgres`_ as a database engine. Provide database replication for fixtures.
    Tested with Postgres v8.2

* `Python-PostgreSQL database driver`_. Provide access to postgres database.
    Tested with psycopg2 v2.0.5



.. _django-selenium-test-runner: http://pypi.python.org/pypi/django-selenium-test-runner
.. _Selenium web testing tools: http://seleniumhq.org/
.. _selenium-ide: http://seleniumhq.org/movies/intro.mov
.. _Fixtures: http://docs.djangoproject.com/en/dev/howto/initial-data/
.. _setuptools: http://pypi.python.org/pypi/setuptools
.. _tutorial: http://docs.djangoproject.com/en/dev/intro/tutorial01/
.. _Selenium RC server and python driver: http://release.seleniumhq.org/selenium-remote-control/1.0.1/selenium-remote-control-1.0.1-dist.zip
.. _CherryPy WSGI multi-thread web server: http://www.cherrypy.org/wiki/CherryPyInstall
.. _Django mediahandler.py: http://www.arteme.fi/blog/2009/02/26/django-cherrypy-dev-server-and-static-files
.. _Python 2.x: http://www.python.org/download/
.. _Django 1.x: http://docs.djangoproject.com/en/dev/topics/install/
.. _Java VM command line runner: http://openjdk.java.net/install/
.. _Postgres: http://www.postgresql.org/download/
.. _Python-PostgreSQL database driver: http://pypi.python.org/pypi/psycopg2/