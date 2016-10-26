# coding: utf8
"""
Main command line interface of the cdstarcat package.

The basic invocation looks like

    cdstarcat [OPTIONS] <command> [args]

"""
from __future__ import unicode_literals, print_function
import sys
from collections import Counter
from itertools import groupby, chain
import os

from clldutils.clilib import ArgumentParser
from clldutils.markup import Table

from cdstarcat.catalog import Catalog, OBJID_PATTERN


def cleanup(args):
    with _catalog(args) as cat:
        n = len(cat)
        for obj in cat:
            if not obj.bitstreams:
                if obj.is_special:
                    print('removing {0} from catalog'.format(obj.id))
                    cat.remove(obj)
                else:
                    print('deleting {0} from CDSTAR'.format(obj.id))
                    cat.delete(obj)
        print('{0} objects deleted'.format(n - len(cat)))


def stats(args):
    cat = _catalog(args)
    print('Summary:')
    print('  {0:,} objects with {1:,} bitstreams of total size {2}'.format(
        len(cat), sum(len(obj.bitstreams) for obj in cat), cat.size_h))
    print('  {0} duplicate bitstreams'.format(
        sum(1 for objs in cat.md5_to_object.values() if len(objs) > 1)))
    print('  {0} objects with no bitstreams'.format(
        sum(1 for obj in cat if not obj.bitstreams)))

    print()
    types = Counter(chain(*[[bs.mimetype for bs in obj.bitstreams] for obj in cat]))
    table = Table('maintype', 'subtype', 'bitstreams')
    for maintype, items in groupby(
            sorted(types.items(), key=lambda p: (p[0].split('/')[0], -p[1])),
            lambda p: p[0].split('/')[0]):
        for k, v in items:
            table.append([maintype, k.split('/')[1], v])
    print(table.render(tablefmt='simple'))


def add(args):
    spec = args.args[0]
    with _catalog(args) as cat:
        n = len(cat)
        if OBJID_PATTERN.match(spec):
            cat.add_objids(spec)
        else:
            results = cat.add_query(spec)
            print('{0} hits for query {1}'.format(results, spec))
        print('{0} objects added'.format(len(cat) - n))


def create(args):
    with _catalog(args) as cat:
        for fname, created, obj in cat.create(args.args[0], {}):
            print('{0} -> {1} object {2.id}'.format(
                fname, 'new' if created else 'existing', obj))


def delete(args):
    with _catalog(args) as cat:
        n = len(cat)
        cat.delete(args.args[0])
        print('{0} objects deleted'.format(n - len(cat)))


def update(args):
    with _catalog(args) as cat:
        cat.update_metadata(
            args.args[0], dict([arg.split('=', 1) for arg in args.args[1:]]))


def _catalog(args):
    return Catalog(args.catalog, args.url, args.user, args.pwd)


def main():  # pragma: no cover
    parser = ArgumentParser(__name__, stats, add, cleanup, create, delete, update)
    for arg in ['catalog', 'url', 'user', 'pwd']:
        envvar = 'CDSTAR_{0}'.format(arg.upper())
        parser.add_argument(
            '--' + arg,
            help="defaults to ${0}".format(envvar),
            default=os.environ.get(envvar))
    sys.exit(parser.main())
