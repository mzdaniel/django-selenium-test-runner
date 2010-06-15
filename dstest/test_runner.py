"""Django Selenium test runner.

Incorporate functional testing into Django's manage.py test subcommand
using Selenium web testing tools."""

__author__      = 'Daniel Mizyrycki'
__copyright__   = 'Copyright 2009, Daniel Mizyrycki'
__license__     = 'BSD'
__version__     = '0.1.0'
__maintainer__  = __author__
__email__       = 'mzdaniel@gmail.com'
__status__      = 'Development'
__url__         = 'http://pypi.python.org/pypi/django-selenium-test-runner'
__summary__     = __doc__


from django.conf import settings
from django.core.management import setup_environ, import_module, call_command
if not hasattr(settings, 'SETTINGS_MODULE'):
    settings.configure()
else:
    PROJECT_PATH = setup_environ(import_module(settings.SETTINGS_MODULE),
        settings.SETTINGS_MODULE)

import os, sys, re, threading, unittest, shutil
from urlparse import urlparse
from subprocess import Popen, PIPE
from signal import SIGHUP
from time import sleep
from django.db import connection
from django.db.models import get_app, get_apps
from django.test.simple import run_tests as base_run_tests
from django.core.handlers.wsgi import WSGIHandler
from django.contrib import admin
from wsgiserver import CherryPyWSGIServer, WSGIPathInfoDispatcher
from mediahandler import MediaHandler


SELENIUM_TESTS_PATH = 'tests/selenium'
FIXTURES = ['tests/data.json']
DSTEST_PATH = os.path.dirname(__file__)
TEST_DB_NAME = 'test_fixture_db'
SELENIUM_RC_PATH = os.path.join(DSTEST_PATH, 'selenium-server.jar')
CPSERVER_OPTIONS = {'host': 'localhost', 'port': 8000, 'threads': 10,
    'request_queue_size': 15}

# Overwrite default settings from settings.py if they are defined.
if hasattr(settings, 'SELENIUM_TESTS_PATH'):
    SELENIUM_TESTS_PATH = settings.SELENIUM_TESTS_PATH
if hasattr(settings, 'FIXTURES'):
    FIXTURES = settings.FIXTURES
if hasattr(settings, 'SELENIUM_PATH'):
    SELENIUM_RC_PATH = os.path.join(settings.SELENIUM_PATH,
        'selenium-server.jar')
    sys.path += [settings.SELENIUM_PATH]

sys.path += [DSTEST_PATH]


class SeleniumRCThread(threading.Thread):
    """Selenium RC control thread."""
    def __init__(self, server_filepath):
        super(SeleniumRCThread, self).__init__()
        self.server_filepath = server_filepath
        self.process = None

    def run(self):
        """Launch Selenium server."""
        self.process = Popen(('java -jar %s' % self.server_filepath).split(),
            shell=False, stdout=PIPE, stderr=PIPE)

    def stop(self):
        """Stop Selenium server."""
        os.kill(self.process.pid, SIGHUP)


class TestDB(object):
    """Encapsulate fixtured database handling for tests to be used by
    Django web server. As the Django connection is global, this class will
    setup TEST_DB_NAME as the database in use."""

    def __init__(self, db_name, fixtures, verbosity=0):
        """Initialize TestDB."""
        self.db_name = db_name
        self.fixtures = fixtures
        self.verbosity = verbosity
        # Save the real database names for later connection restore.
        self.database_name = settings.DATABASE_NAME
        self.test_database_name = settings.TEST_DATABASE_NAME
        self.db_path = None
        self.db_backup_path = None

    def initialize_test_db(self):
        """Establish a connection to a fresh TEST_DB_NAME database with the
        test fixtures on it."""
        # Create a test database and sync it with models.py
        # Handle a second test database for selenium use. Postgres uses
        # transactions which interfere with the Django server thread.
        settings.TEST_DATABASE_NAME = self.db_name
        connection.creation.create_test_db(verbosity=self.verbosity,
            autoclobber=True)
        # Hook for doing any extra initialization
        self.extra_init()
        # Load fixture data.
        call_command('loaddata', *self.fixtures, verbosity=self.verbosity)
        # Sync data and close connection
        connection.close()
        # If sqlite3 or Postgres is used, create a backup database to speed up
        # fixture reloading.
        if settings.DATABASE_ENGINE == 'postgresql_psycopg2':
            # connection.creation is used to overcome transaction management,
            # allowing to execute DROP and CREATE db commands.
            cursor = connection.cursor()
            connection.creation.set_autocommit()
            cursor.execute("DROP DATABASE IF EXISTS %s_backup" % self.db_name)
            cursor.execute("CREATE DATABASE %s_backup WITH TEMPLATE %s" % (
                self.db_name, self.db_name))
        if settings.DATABASE_ENGINE == 'sqlite3':
            self.db_path = os.path.join(PROJECT_PATH, settings.DATABASE_NAME)
            self.db_backup_path = '%s_backup' % self.db_path
            if self.db_path[-3:] == '.db':
                self.db_backup_path = '%s_backup.db' % self.db_path[:-3]
            shutil.copyfile(self.db_path, self.db_backup_path)
        # Restore the database names as create_test_db changed it.
        settings.TEST_DATABASE_NAME = self.test_database_name
        settings.DATABASE_NAME = self.database_name

    def extra_init(self):
        """Hook for doing any extra initialization. After subclassing TestDB,
        and overriding this method, initialize_test_db will call it."""
        pass

    def reload_db(self):
        """Reload fixtures into test database. This is a database dependant
        method. For now, only works on Postgres."""
        if not settings.DATABASE_ENGINE in ['sqlite3', 'postgresql_psycopg2']:
            return None
        # Close connection to cleanly swap databases.
        connection.close()
        if settings.DATABASE_ENGINE == 'sqlite3':
            shutil.copyfile(self.db_backup_path, self.db_path)
        if settings.DATABASE_ENGINE == 'postgresql_psycopg2':
            # Establish a temporal connection to template1 database and
            # recreate TEST_DB_NAME.
            connection.settings_dict["DATABASE_NAME"] = 'template1'
            cursor = connection.cursor()
            connection.creation.set_autocommit()
            cursor.execute("DROP DATABASE IF EXISTS %s" % self.db_name)
            cursor.execute("CREATE DATABASE %s WITH TEMPLATE %s_backup" % (
                self.db_name, self.db_name))
            connection.close()
        # Change the connection to the new test database.
        settings.DATABASE_NAME = self.db_name
        connection.settings_dict["DATABASE_NAME"] = self.db_name
        # Get a cursor (even though we don't need one yet). This has
        # the side effect of initializing the test database.
        connection.cursor()
        return True

    def drop(self):
        """Drop test database. This is a database dependant method. For now,
        only works on Postgres."""

        def drop_db(name):
            """TestDB.drop helper function"""
            try:
                connection.creation._destroy_test_db(name, verbosity=0)
            except:
                return None
            return True

        if not settings.DATABASE_ENGINE in ['sqlite3', 'postgresql_psycopg2']:
            return None
        connection.close()
        if settings.DATABASE_ENGINE == 'postgresql_psycopg2':
            connection.settings_dict["DATABASE_NAME"] = 'template1'
        drop_db('%s_backup' % self.db_name)
        drop_db(self.db_name)
        drop_db(self.test_database_name)
        # restore the connection to the original database.
        settings.TEST_DATABASE_NAME = self.test_database_name
        settings.DATABASE_NAME = self.database_name
        connection.settings_dict["DATABASE_NAME"] = self.database_name
        connection.cursor()


class DjangoThread(threading.Thread):
    """Django server control thread."""
    def __init__(self, testdb):
        """Initialize CherryPy Django web server."""
        super(DjangoThread, self).__init__()
        testdb.initialize_test_db()
        self.setDaemon(True)

    def run(self):
        """Launch CherryPy Django web server."""
        options = CPSERVER_OPTIONS
        server = CherryPyWSGIServer(
            (options['host'], int(options['port'])),
            WSGIPathInfoDispatcher({
                '/': WSGIHandler(),
                urlparse(settings.MEDIA_URL).path: MediaHandler(
                    settings.MEDIA_ROOT),
                settings.ADMIN_MEDIA_PREFIX: MediaHandler(
                    os.path.join(admin.__path__[0], 'media'))
            }),
            int(options['threads']), options['host'],
            request_queue_size=int(options['request_queue_size']))
        try:
            server.start()
        except KeyboardInterrupt:
            server.stop()


def get_selenium_tests(testdb, test_labels=None):
    """Import selenium tests stored on path/SELENIUM_TESTS_PATH."""

    def load_tests(module_path):
        """Import selenium tests."""

        def add_fixtures(ctest):
            """Monkeypatch selenium tests to add django fixtures."""

            def test_setup(funct):
                """Test setUp decorator to add fixture reloading."""

                def decorated_setup():
                    """Decorated test setup."""
                    testdb.reload_db()
                    funct()
                return decorated_setup

            for test in ctest._tests:
                test.setUp = test_setup(test.setUp)

        # Check dependencies before loading test.
        tests = []
        test_path = os.path.join(module_path, SELENIUM_TESTS_PATH)
        if not os.path.isdir(test_path):
            return tests
        sys.path += [test_path]
        # Monkeypatch selenium tests to reload fixtures into Django server db.
        for filename in os.listdir(test_path):
            if not re.search('^test_.+\.py$', filename):
                continue
            test_module = __import__(filename[:-len('.py')])
            # Add all unittests from module
            for test_name in test_module.__dict__:
                test_case = test_module.__dict__[test_name]
                if not (type(test_case) is type(unittest.TestCase) and \
                 issubclass(test_case, unittest.TestCase)):
                    continue
                test = unittest.TestLoader().loadTestsFromTestCase(test_case)
                # Setup fixtures for the test.
                add_fixtures(test)
                tests.append(test)
        return tests

    tests = []
    if test_labels:
        for label in test_labels:
            tests += load_tests(os.path.dirname(get_app(label).__file__))
    else:
        for app in get_apps():
            tests += load_tests(os.path.dirname(app.__file__))
    return tests


def dependencies_met():
    """Check Selenium testing dependencies are met"""
    # Check Java VM command line runner.
    try:
        Popen(['java'], shell=False, stderr=PIPE).communicate()[1]
    except:
        print 'Dependecy unmet. Java virtual machine command line runner not ' \
            'found.'
        return False
    # Check selenium-server.jar is ready to run.
    output = Popen(('java -jar %s -unrecognized_argument' % SELENIUM_RC_PATH
        ).split(), shell=False, stderr=PIPE).communicate()[1]
    if not re.search('Usage: java -jar selenium-server.jar', output):
        print 'Dependecy unmet. Selenium RC server (selenium-server.jar) not ' \
            'found.'
        return False
    # Check selenium RC python driver is available.
    try:
        import selenium
    except:
        print 'Dependecy unmet. Selenium RC python driver (selenium.py) not ' \
            'found.'
        return False
    # Check CherryPy wsgi server is available.
    try:
        import wsgiserver
    except:
        print 'Dependecy unmet. CherryPy wsgi server (wsgiserver.py) not found.'
        return False
    # Check fixture support is implemented for the database engine.
    if not settings.DATABASE_ENGINE in ['sqlite3', 'postgresql_psycopg2']:
        print 'Dependecy unmet. Fixture support for database engine %s not ' \
            'implemented.' % settings.DATABASE_ENGINE
        return False
    return True


def run_tests(test_labels, verbosity=1, interactive=True, extra_tests=None):
    """Selenium Test runner."""
    if not extra_tests:
        extra_tests = []
    dependencies = dependencies_met()
    if dependencies and not extra_tests:
        # Obtain a database test handler.
        testdb = TestDB(TEST_DB_NAME, FIXTURES, verbosity=0)
        extra_tests = get_selenium_tests(testdb, test_labels)
    if dependencies and extra_tests:
        print 'Preparing to run unittests and selenium tests.'
        # Start selenium rc and Django servers.
        selenium_rc = SeleniumRCThread(SELENIUM_RC_PATH)
        selenium_rc.start()
        django_server = DjangoThread(testdb)
        django_server.start()
        # Wait a couple of seconds for the servers to initialize.
        sleep(5)
    else:
        extra_tests = []
        print 'Running unittests but not selenium tests.'
    results = base_run_tests(test_labels, verbosity, interactive, extra_tests)
    if extra_tests:
        # Stop selenium server, and drop test database
        selenium_rc.stop()
        testdb.drop()
    return results
