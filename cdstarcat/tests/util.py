# coding: utf8
from __future__ import unicode_literals, print_function, division

from mock import Mock
from pycdstar.media import File
from clldutils.path import Path, copy
from clldutils.testing import WithTempDir


OBJID = "EAEA0-0005-07E0-246C-0"
PATH = Path(__file__).parent.joinpath('fixtures', 'catalog.json')


class WithTempCatalog(WithTempDir):
    def setUp(self):
        WithTempDir.setUp(self)
        self.catalog_path = self.tmp_path('cat.json')
        copy(PATH, self.catalog_path)


class CdstarObject(object):
    metadata = Mock(read=Mock(return_value={}))
    bitstreams = [Mock(_properties={
        'bitstreamid': 'the.txt',
        'filesize': 5,
        'checksum': 'abcdefg',
        'checksum-algorithm': 'MD5',
        'content-type': 'text/plain',
        'created': 5,
        'last-modified': 7})]

    def __init__(self, id_='12345-1234-1234-1234-1'):
        self.id = id_

    def delete(self):
        return

    def add_bitstream(self, fname=None, **kw):
        f = File(fname)
        self.bitstreams.append(Mock(_properties={
            'bitstreamid': f.clean_name,
            'filesize': f.size,
            'checksum': f.md5,
            'checksum-algorithm': 'MD5',
            'content-type': 'text/plain',
            'created': 5,
            'last-modified': 7}))


class MockApi(object):
    def __init__(self, obj=None, side_effect=None):
        self.obj = obj
        self.side_effect = side_effect
        self.search_called = 0

    def __call__(self, *args, **kw):
        return self

    def get_object(self, *args):
        if self.obj:
            return self.obj
        if self.side_effect:
            raise self.side_effect()

    def search(self, *args, **kw):
        self.search_called += 1
        if self.search_called < 2:
            return [Mock(resource=CdstarObject())]
        return []
