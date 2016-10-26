# coding: utf8
from __future__ import unicode_literals, print_function, division

from mock import Mock, patch
from clldutils.testing import capture

from cdstarcat.tests.util import MockApi, CdstarObject, WithTempCatalog


class Tests(WithTempCatalog):
    def _make_args(self, *args):
        return Mock(args=list(args), catalog=self.catalog_path.as_posix())

    def test_stats(self):
        from cdstarcat.cli import stats

        with capture(stats, self._make_args()) as out:
            self.assertIn('1 objects with 3 bitstreams', out)

    def test_add_delete(self):
        from cdstarcat.cli import delete, add

        obj = CdstarObject()
        with patch('cdstarcat.catalog.Cdstar', MockApi(obj=obj)):
            with capture(add, self._make_args(obj.id)) as out:
                self.assertIn('1 objects added', out)

            with capture(delete, self._make_args(obj.id)) as out:
                self.assertIn('1 objects deleted', out)
