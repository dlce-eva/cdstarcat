"""
Print summary statistics of bitstreams in the catalog to stdout.
"""
import itertools
import collections

from clldutils.clilib import Table, add_format


def register(parser):  # pylint: disable=C0116
    add_format(parser, default='simple')


def run(args):  # pylint: disable=C0116
    nbitstreams = sum(len(obj.bitstreams) for obj in args.catalog)
    print('Summary:')
    print(f'  {len(args.catalog):,} objects with {nbitstreams:,} '
          f'bitstreams of total size {args.catalog.size_h}')
    duplicates = sum(1 for objs in args.catalog.md5_to_object.values() if len(objs) > 1)
    print(f'  {duplicates} duplicate bitstreams')
    print(f'  {sum(1 for obj in args.catalog if not obj.bitstreams)} objects with no bitstreams')

    print()
    types = collections.Counter(itertools.chain(
        *[[bs.mimetype for bs in obj.bitstreams] for obj in args.catalog]))
    with Table(args, 'maintype', 'subtype', 'bitstreams') as table:
        for maintype, items in itertools.groupby(
                sorted(types.items(), key=lambda p: (p[0].split('/')[0], -p[1])),
                lambda p: p[0].split('/')[0]):
            for k, v in items:
                table.append([maintype, k.split('/')[1], v])
