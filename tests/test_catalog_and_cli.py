import time
import logging
import pathlib
import datetime
import collections

import pytest
from clldutils import jsonlib
from clldutils.path import Path
from pycdstar import media

from cdstarcat.catalog import Catalog, Object, filter_hidden
from cdstarcat.__main__ import main

OBJID = "EAEA0-0005-07E0-246C-0"


@pytest.fixture
def new_catalog(tmpdir):
    return Catalog(str(tmpdir.join('new.json')))


def _patch_api(tmpdir, mocker, cdstar_object, obj=None, side_effect=None):
    class MockApi(object):
        def __init__(self, obj=None, side_effect=None):
            self.obj = obj
            self.side_effect = side_effect
            self.search_called = 0

        def __call__(self, *args, **kw):
            return self

        def get_object(self, *args, **kw):
            if self.obj:
                if args and isinstance(args[0], str):
                    self.obj.id = args[0]
                return self.obj
            if self.side_effect:
                raise self.side_effect()

        def search(self, *args, **kw):
            self.search_called += 1
            if self.search_called < 2:
                return [mocker.Mock(resource=cdstar_object())]
            return []

    mocker.patch('cdstarcat.catalog.Cdstar', MockApi(obj=obj, side_effect=side_effect))
    return Catalog(str(tmpdir.join('new.json')))


def test_getitem(catalog_path):
    cat = Catalog(catalog_path)
    with pytest.raises(KeyError):
        _ = cat['xyz']

    assert len(cat['49fef1d6a6df8e1342efd2e49f12f78f']) == 1


def test_misc(tmpdir):
    assert not filter_hidden(Path(str(tmpdir)) / '.hiddenä')
    assert filter_hidden(Path(str(tmpdir.join('not_hidden'))))


def test_context_manager(tmp_catalog_path):
    jsonlib.dump({}, str(tmp_catalog_path))
    mtime = tmp_catalog_path.mtime()
    with Catalog(str(tmp_catalog_path)):
        time.sleep(0.1)
    assert tmp_catalog_path.mtime() > mtime


def test_idempotency(catalog_path, tmp_catalog_path):
    with catalog_path.open(encoding='utf8') as fp:
        orig = fp.read()
    with Catalog(str(tmp_catalog_path)) as c:
        obj = c[OBJID].asdict()
        obj['metadata'] = collections.OrderedDict(sorted(obj['metadata'].items(), reverse=True))
        c[OBJID] = Object.fromdict(OBJID, obj)
    assert orig.split() == tmp_catalog_path.read_text('utf8').split()


def test_attrs(catalog_path):
    cat = Catalog(catalog_path)
    assert OBJID in cat
    assert cat[OBJID].bitstreams[0].md5 in cat
    assert cat.size_h == '109.8KB'
    assert cat[OBJID].bitstreams[0].modified_datetime < datetime.datetime.now()
    assert cat[OBJID].bitstreams[0].created_datetime < datetime.datetime.now()
    assert not cat[OBJID].is_special


def test_checks(tmp_catalog_path):
    c = Catalog(str(tmp_catalog_path))
    with pytest.raises(ValueError):
        c['objid'] = 1

    with pytest.raises(ValueError):
        c['12345-1234-1234-1234-1'] = 1


def test_empty(tmpdir, tmp_catalog_path, catalog_path):
    with Catalog(str(tmpdir.join('new.json'))) as cat1:
        assert len(cat1) == 0
        cat1[OBJID] = Catalog(catalog_path)[OBJID]
    assert len(Catalog(str(tmp_catalog_path))) == 2


def test_create_read_zipped_json(tmpdir, zipped_catalog_path):
    p = str(tmpdir.join('new.json.zip'))
    with Catalog(p) as cat1:
        assert len(cat1) == 0
        cat1[OBJID] = Catalog(zipped_catalog_path)[OBJID]
    with Catalog(p) as cat1:
        assert len(cat1) == 1
        assert cat1[OBJID].metadata['collection'] == 'tsammalex'


def test_add_remove(new_catalog, cdstar_object):
    assert new_catalog.size == 0
    obj = new_catalog.add(cdstar_object())
    assert new_catalog.size > 0
    new_catalog.remove(obj)
    assert new_catalog.size == 0


def test_delete(tmpdir, mocker, cdstar_object):
    new_catalog = _patch_api(tmpdir, mocker, cdstar_object, obj=cdstar_object())
    obj = new_catalog.add(cdstar_object())
    assert obj in new_catalog
    new_catalog.delete(obj)
    assert obj not in new_catalog


def test_delete_fails(mocker, tmpdir, cdstar_object):
    new_catalog = _patch_api(tmpdir, mocker, cdstar_object, side_effect=ValueError)
    obj = new_catalog.add(cdstar_object())
    with pytest.raises(ValueError):
        new_catalog.delete(obj)
    assert obj in new_catalog


def test_add_objids(mocker, tmpdir, cdstar_object):
    new_catalog = _patch_api(tmpdir, mocker, cdstar_object, obj=cdstar_object())
    new_catalog.add_objids(cdstar_object().id)
    assert len(new_catalog) > 0


def test_add_query(mocker, tmpdir, cdstar_object):
    new_catalog = _patch_api(tmpdir, mocker, cdstar_object)
    new_catalog.add_query('*')
    assert len(new_catalog) > 0


def test_update_metadata(mocker, catalog_path, cdstar_object, tmpdir):
    _patch_api(tmpdir, mocker, cdstar_object, obj=cdstar_object(OBJID))
    cat = Catalog(catalog_path)
    assert 'collection' in cat[OBJID].metadata
    cat.update_metadata(OBJID, {}, mode='replace')
    assert 'collection' not in cat[OBJID].metadata


def test_create(mocker, tmpdir, catalog_path, cdstar_object):
    new_catalog = _patch_api(tmpdir, mocker, cdstar_object, obj=cdstar_object())
    res = list(new_catalog.create(catalog_path, {}))
    assert len(res) == 1
    assert res[0][1]

    res = list(new_catalog.create(catalog_path, {}))
    assert not res[0][1]

    res = list(new_catalog.create(catalog_path.parent.parent, {}))
    assert len(res) > 1

    res = list(new_catalog.create(catalog_path, {}, object_class=media.Audio))
    assert len(res[0][2].bitstreams) == 2


def test_cli_help(capsys):
    main([])
    out, _ = capsys.readouterr()
    assert 'usage' in out


def test_cli_stats(catalog_path, capsys):
    main(['--catalog', str(catalog_path), 'stats'])

    out, _ = capsys.readouterr()
    assert '2 objects with 3 bitstreams' in out


def test_cli_download(catalog_path, tmp_path, mocker, caplog):
    def mock_urlretrieve(url, p):
        pathlib.Path(p).write_text('abc')

    mocker.patch('cdstarcat.commands.download.urlretrieve', mock_urlretrieve)
    main(['--catalog', str(catalog_path), 'download', str(tmp_path)])
    assert tmp_path.joinpath('EAEA0-0005-07E0-246C-0', 'full.jpg').exists()

    with caplog.at_level(logging.WARNING):
        main(
            ['--catalog', str(catalog_path), 'download', str(tmp_path), '--check-md5'],
            log=logging.getLogger(__name__))
    assert len(caplog.records) > 1


def test_cli_cleanup(mocker, tmpdir, cdstar_object, capsys, tmp_catalog_path):
    obj = cdstar_object()
    _patch_api(tmpdir, mocker, cdstar_object, obj=obj)

    main(['--catalog', str(tmp_catalog_path), 'cleanup'])
    out, _ = capsys.readouterr()
    assert 'deleting' in out


def test_add_delete(mocker, tmpdir, cdstar_object, capsys, tmp_catalog_path):
    obj = cdstar_object()
    _patch_api(tmpdir, mocker, cdstar_object, obj=obj)

    main(['--catalog', str(tmp_catalog_path), 'add', obj.id])
    main(['--catalog', str(tmp_catalog_path), 'delete', obj.id])
    main(['--catalog', str(tmp_catalog_path), 'add', 'abc'])

    with pytest.raises(SystemExit):
        main(['--catalog', str(tmp_catalog_path), 'delete', 'abc'])


def test_cli_update(mocker, tmpdir, cdstar_object, tmp_catalog_path):
    obj = cdstar_object()
    _patch_api(tmpdir, mocker, cdstar_object, obj=obj)
    main(['--catalog', str(tmp_catalog_path), 'update', 'EAEA0-0005-07E0-246C-0', 'name=x'])


def test_cli_create(mocker, tmpdir, cdstar_object, tmp_catalog_path, caplog):
    caplog.set_level(logging.INFO)
    obj = cdstar_object()
    _patch_api(tmpdir, mocker, cdstar_object, obj=obj)
    main(['--catalog', str(tmp_catalog_path), 'create', __file__], log=logging.getLogger())
    assert any('new object' in r.msg for r in caplog.records)


def test_add_rollingblob(tmp_catalog_path, cdstar_object, mocker, tmpdir):
    obj = cdstar_object()
    _patch_api(tmpdir, mocker, cdstar_object, obj=obj)
    cat = Catalog(str(tmp_catalog_path))
    cat.add_rollingblob(
        __file__, oid=obj.id, timestamp='20191212T202020Z', suffix='zip', mimetype='text/html')
