"""
Deletes objects with no bitstreams from CDSTAR and the catalog.
"""


def register(parser):  # pylint: disable=C0116
    parser.add_argument(
        '--dry-run',
        action='store_true',
        default=False,
        help='Only list objects to be deleted.',
    )


def run(args):  # pylint: disable=C0116
    n, d, r = len(args.catalog), [], []
    for obj in args.catalog:
        if not obj.bitstreams:
            if obj.is_special:  # pragma: no cover
                print(f'removing {obj.id} from catalog')
                r.append(obj)
            else:
                print(f'deleting {obj.id} from CDSTAR')
                d.append(obj)
    if not args.dry_run:
        for obj in d:
            args.catalog.delete(obj)
        for obj in r:  # pragma: no cover
            args.catalog.remove(obj)
    args.log.info(f'{n - len(args.catalog)} objects deleted')
    return n - len(args.catalog)
