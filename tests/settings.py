DATABASE_ENGINE = 'sqlite3'
DATABASE_NAME = 'mysite.db'
ROOT_URLCONF = 'urls'
SITE_ID = 1

DEBUG = True
INSTALLED_APPS = (
    'django.contrib.contenttypes',
    'django.contrib.auth',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.admin',
    'polls')

TEST_RUNNER='dstest.test_runner.run_tests'
