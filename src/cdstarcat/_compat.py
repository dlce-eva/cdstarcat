"""
Functionality ensuring backwards compatibility with still supported python versions.
"""
import sys
import datetime
import functools


if (sys.version_info.major, sys.version_info.minor) >= (3, 11):  # pragma: no cover
    # datetime.UTC was added in py3.11.
    utcnow = functools.partial(datetime.datetime.now, datetime.UTC)
else:  # pragma: no cover
    utcnow = datetime.datetime.utcnow
