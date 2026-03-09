import sys
import datetime
import functools


if (sys.version_info.major, sys.version_info.minor) >= (3, 11):  # pragma: no cover
    utcnow = functools.partial(datetime.datetime.now, datetime.UTC)
else:  # pragma: no cover
    utcnow = datetime.datetime.utcnow
