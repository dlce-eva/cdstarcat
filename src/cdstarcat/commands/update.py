"""
Update the metadata of an object.
"""
from cdstarcat.cli_util import add_objid


def register(parser):  # pylint: disable=C0116
    add_objid(parser)
    parser.add_argument(
        'props',
        metavar='KEY_VALUE',
        nargs='+',
        help='Object property given as "KEY=VALUE"',
    )


def run(args):  # pylint: disable=C0116
    args.catalog.update_metadata(args.objid, dict([arg.split('=', 1) for arg in args.props]))
