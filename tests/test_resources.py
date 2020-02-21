import pytest

from cdstarcat import resources


@pytest.fixture
def cdstar(mocker):
    class Bitstream(object):
        def __init__(self, id_):
            self.id = id_

        def delete(self):
            pass
    return mocker.Mock(get_object=lambda **kw: mocker.Mock(
        bitstreams=[Bitstream('0081212T010101'), Bitstream('20181212T010101Z')],
        metadata=mocker.Mock(read=lambda: {'collection': 'c', 'name': 'n'})))


def test_RollingBlob_init():
    with pytest.raises(ValueError):
        resources.RollingBlob(name='y')

    with pytest.raises(ValueError):
        resources.RollingBlob(oid='x', name='y')

    resources.RollingBlob(oid='x')


def test_RollingBlob_get_object(mocker):
    rb = resources.RollingBlob(name='name', collection='collection')
    obj = rb.get_object(mocker.Mock())
    assert obj.metadata['collection'] == 'collection'


def test_RollingBlob_get_object2(cdstar):
    rb = resources.RollingBlob(oid='x')
    rb.get_object(cdstar)
    assert rb.collection == 'c'


def test_RollingBlob_latest(cdstar):
    rb = resources.RollingBlob(oid='x')
    assert rb.latest(cdstar).id == '20181212T010101Z'


def test_RollingBlob_expunge(cdstar):
    rb = resources.RollingBlob(oid='x')
    assert rb.expunge(cdstar, keep=1) == 1


def test_RollingBlob_add(cdstar):
    rb = resources.RollingBlob(oid='x')

    with pytest.raises(ValueError):
        rb.add(cdstar, None, suffix='_')

    rb.add(cdstar, None)
