import pathlib

from cdstarcat.catalog import Catalog


def main(p, url, user, pwd):
    objid = None
    with Catalog(p, url, user, pwd, debug=True) as cat:
        for fname, _, obj in cat.create('README.md', dict(creator='someone')):
            objid = obj.id
            break
        assert str(fname) == 'README.md', fname
        assert objid in cat
        cat.update_metadata(objid, dict(creator='test'))

    with Catalog(p, url, user, pwd, debug=True) as cat:
        assert objid in cat
        obj = cat[objid]
        assert obj.metadata['creator'] == 'test'
        cat.delete(obj)
        assert objid not in cat

    p.unlink()


if __name__ == '__main__':
    import os
    main(
        pathlib.Path('test_cat.json'),
        os.environ['CDSTAR_URL'],
        os.environ['CDSTAR_USER'],
        os.environ['CDSTAR_PWD'])
