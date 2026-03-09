"""
Create objects in CDSTAR (and record them in the catalog).
"""
from clldutils.clilib import PathType


def register(parser):  # pylint: disable=C0116
    parser.add_argument(
        'path',
        type=PathType(),
        help="Path to file or directory to create CDSTAR object(s) for. When PATH is a file, "
             "a single object (possibly with multiple bitstreams) is created; when PATH is a "
             "directory, an object will be created for each file in the directory "
             "(recursing into subdirectories).",
        metavar='PATH')


def run(args):  # pylint: disable=C0116
    for fname, created, obj in args.catalog.create(args.path, {}):
        args.log.info(f"{fname} -> {'new' if created else 'existing'} object {obj.id}")
