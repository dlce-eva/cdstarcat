# cdstarcat

[![Build Status](https://travis-ci.org/clld/cdstarcat.svg?branch=master)](https://travis-ci.org/clld/cdstarcat)
[![codecov](https://codecov.io/gh/clld/cdstarcat/branch/master/graph/badge.svg)](https://codecov.io/gh/clld/cdstarcat)
[![Requirements Status](https://requires.io/github/clld/cdstarcat/requirements.svg?branch=master)](https://requires.io/github/clld/cdstarcat/requirements/?branch=master)
[![PyPI](https://img.shields.io/pypi/v/cdstarcat.svg)](https://pypi.python.org/pypi/cdstarcat)

Manage objects in a CDSTAR instance using a local catalog.


## Install

Running
```shell
pip install cdstarcat
```

will install the `cdstarcat` package as well as a commandline interface `cdstarcat`.

For developing `cdstarcat`, clone the repository `clld/cdstarcat` and run
```shell
cd cdstarcat
pip install -r requirements.txt
```


## CLI

Run
```shell
cdstarcat --help
```
to get a list of available subcommands, and
```shell
cdstarcat help SUBCOMMAND
```
to get usage information for a particular subcommand.


## cdstarcat API

Typically, `cdstarcat` will be used programmatically, to implement recurring media file maintenance tasks
within projects - such as 
[uploading media files for a new submission to Dictionaria](https://github.com/clld/dictionaria-intern/blob/292644d23c0495d5a339bae1a0696ffe3129dcbf/pydictionaria/commands.py#L22-L42).

In the simplest case this could look as follows:
```python
import os
from cdstarcat import Catalog

def upload(directory):
    with Catalog(
        os.environ['CDSTAR_CATALOG'],
        cdstar_url=os.environ['CDSTAR_URL'],
        cdstar_user=os.environ['CDSTAR_USER'],
        cdstar_pwd=os.environ['CDSTAR_PWD']
    ) as cat:
        md = {
            'collection': 'PROJECT NAME',
            'path': '%s' % directory,
        }
        for fname, created, obj in cat.create(directory, md):
            print('{0} -> {1}'.format(fname, obj.id))
```
