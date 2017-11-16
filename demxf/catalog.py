import struct

from demxf.chunk import Chunk


class CatalogEntry:
    def __init__(self, chunk):
        self.chunk = chunk
        self.data = chunk.get_child_dict(data_only=True)

    @property
    def type(self):
        return self.data[b'type'].strip(b'\x00').decode().strip()

    @property
    def filename(self):
        return self.data[b'fnam'].strip(b'\x00').decode()

    @property
    def size(self):
        return struct.unpack('>I', self.data[b'sz32'])[0]

    @property
    def offset(self):
        return struct.unpack('>I', self.data[b'of32'])[0]

    @property
    def version(self):
        return struct.unpack('>I', self.data[b'vers'])[0]

    def extract_from(self, fp):
        fp.seek(self.offset)
        return fp.read(self.size)


def read_mxf_catalog(infp):
    magic = infp.read(4)
    assert magic == b'mx@c'
    header = infp.read(12)
    a, b, c = struct.unpack('>III', header)
    infp.seek(c)
    dlist = Chunk.read(infp)
    assert dlist.type == b'dlst'
    return [CatalogEntry(chunk) for chunk in dlist.get_children() if chunk.type == b'dire']
