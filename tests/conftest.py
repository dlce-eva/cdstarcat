import pathlib

import py
import pytest
from mock import Mock

from pycdstar.media import File


@pytest.fixture
def catalog_path():
    return pathlib.Path(__file__).parent / 'fixtures' / 'catalog.json'


@pytest.fixture
def zipped_catalog_path():
    return pathlib.Path(__file__).parent / 'fixtures' / 'catalog.json.zip'


@pytest.fixture
def tmp_catalog_path(tmpdir):
    catalog_path = tmpdir.join('cat.json')
    py.path.local(__file__).dirpath('fixtures', 'catalog.json').copy(catalog_path)
    return catalog_path


class CdstarObject(object):
    metadata = Mock(read=Mock(return_value={'name': 'n', 'collection': 'c'}))
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



@pytest.fixture
def cdstar_object():
    return CdstarObject
