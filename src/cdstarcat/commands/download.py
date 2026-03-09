"""
Downloads the bitstreams of an object in the catalog.
"""
from urllib.request import urlretrieve

from tqdm import tqdm
from clldutils.clilib import PathType
from clldutils.path import md5

from cdstarcat.catalog import Object, Bitstream


def register(parser):  # pylint: disable=C0116
    parser.add_argument('--check-md5', action='store_true', default=False)
    parser.add_argument('outdir', type=PathType(type='dir'))


def run(args):  # pylint: disable=C0116
    obj: Object
    bs: Bitstream
    for obj in tqdm(args.catalog):
        for bs in obj.bitstreams:
            p = args.outdir / obj.id / bs.id
            if p.exists() and args.check_md5 and md5(p) != bs.md5:
                args.log.warning('Removing file with wrong checksum: %s', p)
                p.unlink()
            if not p.exists():
                if not p.parent.exists():
                    p.parent.mkdir()
                url = args.catalog.api.url(f'/bitstreams/{obj.id}/{bs.id}')
                urlretrieve(url, str(p))
