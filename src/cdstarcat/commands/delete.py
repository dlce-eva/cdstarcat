"""
Delete an object from CDSTAR (and the catalog).
"""
from cdstarcat.cli_util import add_objid


def register(parser):  # pylint: disable=C0116
    add_objid(parser)


def run(args):  # pylint: disable=C0116
    n = len(args.catalog)
    args.catalog.delete(args.objid)
    args.log.info(f'{n - len(args.catalog)} objects deleted')
    return n - len(args.catalog)
