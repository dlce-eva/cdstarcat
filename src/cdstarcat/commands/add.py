"""
Add metadata about objects (specified by SPEC) in CDSTAR to the catalog.
"""
from cdstarcat.catalog import OBJID_PATTERN


def register(parser):  # pylint: disable=C0116
    parser.add_argument(
        'spec',
        help='Either a CDSTAR object ID or a query',
        metavar='SPEC')
    parser.add_argument(
        '--update',
        action='store_true',
        default=False,
    )


def run(args):  # pylint: disable=C0116
    n = len(args.catalog)
    if OBJID_PATTERN.match(args.spec):
        args.catalog.add_objids(args.spec, update=args.update)
    else:
        results = args.catalog.add_query(args.spec)
        args.log.info('%s hits for query %s', results, args.spec)
    args.log.info('%s objects added', len(args.catalog) - n)
    return len(args.catalog) - n
