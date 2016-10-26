# coding: utf8
from __future__ import unicode_literals, print_function, division
import time
from collections import OrderedDict
import datetime

from clldutils import jsonlib
from mock import patch

from cdstarcat.catalog import Catalog, Object, filter_hidden
from cdstarcat.tests.util import PATH, OBJID, CdstarObject, MockApi, WithTempCatalog


class Tests(WithTempCatalog):
    def test_misc(self):
        self.assertFalse(filter_hidden(self.tmp_path('.hidden')))
        self.assertTrue(filter_hidden(self.tmp_path('not_hidden')))

    def test_context_manager(self):
        jsonlib.dump({}, self.catalog_path)
        mtime = self.catalog_path.stat().st_mtime
        with Catalog(self.catalog_path):
            time.sleep(0.1)
        self.assertGreater(self.catalog_path.stat().st_mtime, mtime)

    def test_idempotency(self):
        with PATH.open(encoding='utf8') as fp:
            orig = fp.read()
        with Catalog(self.catalog_path) as c:
            obj = c[OBJID].asdict()
            obj['metadata'] = OrderedDict(sorted(obj['metadata'].items(), reverse=True))
            c[OBJID] = Object.fromdict(OBJID, obj)
        with self.catalog_path.open(encoding='utf8') as fp:
            new = fp.read()
        self.assertEqual(orig.split(), new.split())

    def test_attrs(self):
        cat = Catalog(PATH)
        self.assertIn(OBJID, cat)
        self.assertIn(cat[OBJID].bitstreams[0].md5, cat)
        self.assertEqual(cat.size_h, '109.8KB')
        self.assertLess(
            cat[OBJID].bitstreams[0].modified_datetime,
            datetime.datetime.now())
        self.assertLess(
            cat[OBJID].bitstreams[0].created_datetime,
            datetime.datetime.now())
        self.assertFalse(cat[OBJID].is_special)

    def test_checks(self):
        c = Catalog(self.catalog_path)
        with self.assertRaises(ValueError):
            c['objid'] = 1

        with self.assertRaises(ValueError):
            c['12345-1234-1234-1234-1'] = 1

    def test_empty(self):
        with Catalog(self.tmp_path('new.json')) as cat1:
            self.assertEqual(len(cat1), 0)
            cat1[OBJID] = Catalog(PATH)[OBJID]
        self.assertEqual(len(Catalog(self.tmp_path('cat.json'))), 1)

    def test_add_remove(self):
        c = Catalog(self.tmp_path('new.json'))
        self.assertEqual(c.size, 0)
        obj = c.add(CdstarObject())
        self.assertGreater(c.size, 0)
        c.remove(obj)
        self.assertEqual(c.size, 0)

    def test_delete(self):
        with patch('cdstarcat.catalog.Cdstar', MockApi(obj=CdstarObject())):
            cat = Catalog(self.tmp_path('new.json'))
            obj = cat.add(CdstarObject())
            self.assertIn(obj, cat)
            cat.delete(obj)
            self.assertNotIn(obj, cat)

    def test_delete_fails(self):
        with patch('cdstarcat.catalog.Cdstar', MockApi(side_effect=ValueError)):
            cat = Catalog(self.tmp_path('new.json'))
            obj = cat.add(CdstarObject())
            with self.assertRaises(ValueError):
                cat.delete(obj)
            self.assertIn(obj, cat)

    def test_add_objids(self):
        with patch('cdstarcat.catalog.Cdstar', MockApi(obj=CdstarObject())):
            cat = Catalog(self.tmp_path('new.json'))
            cat.add_objids(CdstarObject().id)
            self.assertGreater(len(cat), 0)

    def test_add_query(self):
        with patch('cdstarcat.catalog.Cdstar', MockApi()):
            cat = Catalog(self.tmp_path('new.json'))
            cat.add_query('*')
            self.assertGreater(len(cat), 0)

    def test_update_metadata(self):
        with patch('cdstarcat.catalog.Cdstar', MockApi(obj=CdstarObject(OBJID))):
            cat = Catalog(PATH)
            self.assertIn('collection', cat[OBJID].metadata)
            cat.update_metadata(OBJID, {}, mode='replace')
            self.assertNotIn('collection', cat[OBJID].metadata)

    def test_create(self):
        with patch('cdstarcat.catalog.Cdstar', MockApi(obj=CdstarObject())):
            cat = Catalog(self.tmp_path('new.json'))
            res = list(cat.create(PATH, {}))
            self.assertEqual(len(res), 1)
            self.assertTrue(res[0][1])

            res = list(cat.create(PATH, {}))
            self.assertFalse(res[0][1])

            res = list(cat.create(PATH.parent.parent, {}))
            self.assertGreater(len(res), 1)
