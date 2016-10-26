# -*- coding: utf-8 -*-
from setuptools import setup, find_packages


def read(fname):
    with open(fname) as fp:
        return fp.read().split('\n\n\n')[0]


setup(
    name='cdstarcat',
    version="0.2.0",
    description='Manage objects in a CDSTAR instance through a catalog',
    long_description=read("README.md"),
    author='Robert Forkel',
    author_email='forkel@shh.mpg.de',
    url='https://github.com/clld/cdstarcat',
    install_requires=[
        'clldutils>=1.4.1',
        'pycdstar>=0.3',
        'attrs',
    ],
    license="Apache 2",
    zip_safe=False,
    keywords='',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy'
    ],
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'cdstarcat=cdstarcat.cli:main',
        ]
    },
    tests_require=['nose', 'coverage', 'mock'],
)
