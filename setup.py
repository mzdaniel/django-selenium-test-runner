from setuptools import setup, find_packages
from dstest import test_runner as mm

setup(
    name='django-selenium-test-runner',
    version=mm.__version__,
    author=mm.__author__,
    author_email=mm.__email__,
    description=mm.__summary__,
    long_description=open('README.txt').read(),
    classifiers=[
        "Programming Language :: Python",
        "License :: OSI Approved :: BSD License",
        "Operating System :: POSIX :: Linux",
        "Development Status :: 3 - Alpha",
        "Environment :: Web Environment",
        "Framework :: Django",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Testing",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    keywords='django selenium testing',
    url=mm.__url__,
    license=mm.__license__,
    packages=find_packages(),
    include_package_data=True,
    package_data = {'': ['*.jar']},
    zip_safe=False,
)
