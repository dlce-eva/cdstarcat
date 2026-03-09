"""
Support for specialized CDSTAR objects.
"""
import datetime
import dataclasses
from typing import Optional, Union

from pycdstar.api import Cdstar
from pycdstar.resource import Object, Bitstream

from ._compat import utcnow

# We use a timestamp format which is compatible with the syntax of CDSTAR bitstream names:
TIMESTAMP_FORMAT = '%Y%m%dT%H%M%SZ'


@dataclasses.dataclass
class RollingBlob:
    """
    RollingBlobs are big(gish), versioned files of which only the last couple of versions need to
    be available (such as log files or database dumps).
    """
    collection: Optional[str] = None
    name: Optional[str] = None
    oid: Optional[str] = None

    def __post_init__(self):
        if not self.oid and not (self.collection and self.name):
            raise ValueError('If no oid is given, collection and name must be specified.')
        if self.oid and (self.collection or self.name):
            raise ValueError('If oid is given, neither collection nor name must be given.')

    @staticmethod
    def parse_timestamp(bsid: str) -> datetime.datetime:
        """Turn the timestamp used to order blobs into a datetime object."""
        try:
            return datetime.datetime.strptime(bsid.split('_')[-1].split('.')[0], TIMESTAMP_FORMAT)
        except (ValueError, TypeError):
            # Make sure invalid timestamps are sorted as earlier than any valid ones.
            return datetime.datetime.strptime('19000101T000000Z', TIMESTAMP_FORMAT)

    def get_object(self, cdstar: Cdstar) -> Object:
        """Get (and possibly create) a CDSTAR object for the collection."""
        obj = cdstar.get_object(uid=self.oid)
        if self.oid is None:
            self.oid = obj.id
            obj.metadata = {
                'collection': self.collection,
                'name': self.name,
                'type': self.__class__.__name__,
            }
        else:
            md = obj.metadata.read()
            self.name = md['name']
            self.collection = md['collection']
        return obj

    def add(self,  # pylint: disable=R0913,R0917
            cdstar: Cdstar,
            fname: str,
            suffix: str = '',
            timestamp: Optional[Union[str, datetime.datetime]] = None,
            mimetype: Optional[str] = None):
        """Add a blob, i.e. a bitstream."""
        if '_' in suffix:
            raise ValueError(suffix)
        timestamp = timestamp or utcnow()
        if isinstance(timestamp, str):
            timestamp = datetime.datetime.strptime(timestamp, TIMESTAMP_FORMAT)
        if suffix and not suffix.startswith('.'):
            suffix = '.' + suffix
        obj = self.get_object(cdstar)
        kw = {'name': f'{self.name}_{timestamp.strftime(TIMESTAMP_FORMAT)}{suffix}', 'fname': fname}
        if mimetype:
            kw['mimetype'] = mimetype
        obj.add_bitstream(**kw)

    def sorted_bitstreams(self, cdstar: Cdstar) -> list[Bitstream]:
        """The bitstreams ordered by timestamp, most recent first."""
        obj = self.get_object(cdstar)
        return sorted(obj.bitstreams, key=lambda bs: self.parse_timestamp(bs.id), reverse=True)

    def latest(self, cdstar) -> Optional[Bitstream]:
        """The most recently added bitstream."""
        res = self.sorted_bitstreams(cdstar)
        if res:
            return res[0]
        return None  # pragma: no cover

    def expunge(self, cdstar: Cdstar, keep: int = 5) -> int:
        """Delete older bitstreams until only `keep` are left."""
        deleted = 0
        for i, bs in enumerate(self.sorted_bitstreams(cdstar)):
            if i + 1 > keep:
                bs.delete()
                deleted += 1
        return deleted
