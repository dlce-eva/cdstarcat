import argparse

from cdstarcat.catalog import OBJID_PATTERN


class OBJIDType(object):
    def __call__(self, string):
        if not OBJID_PATTERN.match(string):
            raise argparse.ArgumentTypeError('No valid OBJID: {0}!'.format(string))
        return string


def add_objid(parser):
    parser.add_argument(
        'objid',
        metavar='OBJID',
        type=OBJIDType(),
        help='ID of an object in CDSTAR',
    )
