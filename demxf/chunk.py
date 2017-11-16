import struct
from io import BytesIO


class Chunk:
    def __init__(self, type, content):
        self.type = type
        self.content = content

    def get_children(self):
        stream = BytesIO(self.content)
        return iter(lambda: self.__class__.read(stream), None)

    def get_child_dict(self, data_only=False):
        return {c.type: (c.content if data_only else c) for c in self.get_children()}

    def __repr__(self):
        return '<%s chunk>' % self.type

    @classmethod
    def read(cls, stream):
        type = stream.read(4)
        if len(type) != 4:
            return None
        size, = struct.unpack('>I', stream.read(4))
        content = stream.read(size - 8)  # size includes name/size bytes
        return cls(type, content)
