#!/usr/bin/env python
# This file is part of django-objs.
import warnings

from setuptools import setup, find_packages

try:
    README = open('README.md').read() + '\n\n'
except:
    warnings.warn('Could not read README.md')
    README = None

try:
    REQUIREMENTS = open('requirements.txt').read()
except:
    warnings.warn('Could not read requirements.txt')
    REQUIREMENTS = None


setup(
    name='django-objs',
    version="0.1",
    description=(
        'Django app for team time tracking and sprint planning, useful for SCRUM.'
    ),
    long_description=README,
    install_requires=REQUIREMENTS,
    license='AGPL',
    author='Daniel Garcia Moreno',
    author_email='danigm@wadobo.com',
    url='http://github.com/wadobo/django-objs/',
    packages=find_packages(exclude=("test_project",)),
    include_package_data=True,
    classifiers=[
        'Development Status :: 6 - Mature',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU Affero General Public License v3',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Utilities'
    ],
)
