import os
import argparse

from cdstarcat.catalog import OBJID_PATTERN


def objid(string):
    if not OBJID_PATTERN.match(string):
        raise argparse.ArgumentTypeError(f'No valid OBJID: {string}!')
    return string


def add_objid(parser):
    """Adds an option to specify a CDSTAR object."""
    parser.add_argument(
        'objid',
        metavar='OBJID',
        type=objid,
        help='ID of an object in CDSTAR',
    )


def add_cdstar(parser):
    """Adds an option to specify a CDSTAR service property."""
    for arg in ['url', 'user', 'pwd']:
        envvar = 'CDSTAR_{arg.upper()}'
        parser.add_argument(
            '--' + arg, help=f"defaults to ${envvar}", default=os.environ.get(envvar))
