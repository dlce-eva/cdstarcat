"""

"""
from urllib.request import urlretrieve

from tqdm import tqdm
from clldutils.clilib import PathType
from clldutils.path import md5


def register(parser):
    parser.add_argument('--check-md5', action='store_true', default=False)
    parser.add_argument('outdir', type=PathType(type='dir'))


def run(args):
    for obj in tqdm(args.catalog):
        for bs in obj.bitstreams:
            p = args.outdir / obj.id / bs.id
            if p.exists() and args.check_md5 and md5(p) != bs.md5:
                args.log.warning('Removing file with wrong checksum: {}'.format(p))
                p.unlink()
            if not p.exists():
                if not p.parent.exists():
                    p.parent.mkdir()
                url = args.catalog.api.url('/bitstreams/{}/{}'.format(obj.id, bs.id))
                urlretrieve(url, str(p))
