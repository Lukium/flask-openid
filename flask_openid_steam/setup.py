"""
Flask-OpenID
============

Adds OpenID support to Flask.

Links:

* `Flask-OpenID Documentation <http://packages.python.org/Flask-OpenID/>`_
* `Flask <http://flask.pocoo.org>`_
* `development version
  <http://github.com/mitsuhiko/flask-openid/zipball/master#egg=Flask-OpenID-dev>`_
"""
from setuptools import setup
import sys
import os

# This check is to make sure we checkout docs/_themes before running sdist
if not os.path.exists("./docs/_themes/README"):
    print('Please make sure you have docs/_themes checked out while running setup.py!')
    if os.path.exists('.git'):
        print('You seem to be using a git checkout, please execute the following commands to get the docs/_themes directory:')
        print(' - git submodule init')
        print(' - git submodule update')
    else:
        print('You seem to be using a release. Please use the release tarball from PyPI instead of the archive from GitHub')
    sys.exit(1)

setup(
    name='Flask-OpenID-Steam',
    version='1.3.1',
    url='http://github.com/lukium/flask-openid/',
    license='BSD',
    author='Armin Ronacher, Patrick Uiterwijk, Jarek Potiuk, Jason R. Coombs, Emmanuel Bavoux, Lukium',
    author_email='armin.ronacher@active-4.com, puiterwijk@redhat.com, jarek@potiuk.com, '
                 'jaraco@jaraco.com, emmanuel.bavoux@free2move.com, mrlukium@outlook.com',
    description='OpenID support for Flask',
    long_description='Patched version of Flask-OpenID to support Steam OpenID without errors.',
    py_modules=['flask_openid_steam'],
    zip_safe=False,
    platforms='any',
    install_requires=['Flask>=0.10.1', 'python3-openid>=2.0'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
    python_requires=">=3.0",
)
