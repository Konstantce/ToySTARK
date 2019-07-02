from algebra.utils import *
import struct

"""
Here we have collected various functions required to construct hashes to points
"""

class ResidueFieldHash():
    def __init__(self, field, seed, base_hash):
        is_residue_field = hasattr(field, "p") and not field.is_extension_field
        if not is_residue_field:
            raise StarkError("Inccorect field")
        if hash.digest <= field.p:
            raise StarkError("Provided hash has too short output")

        self.field = field
        self.seed = seed.encode()
        self.base_hash = base_hash
        self.counter = 0

    def __call__(self):
        digest = base_hash(struct.pack(">q", self.counter) + self.seed)
        self.counter += 1
        return self.field(sum(ord(c) << (i * 8) for i, c in enumerate(digest)))


class BinaryFieldHash():
    def __init__(self, field, seed, base_hash):
        is_binary_field = hasattr(field, "p") and field.p == 2 and field.is_extension_field
        if not is_binary_field:
            raise StarkError("Inccorect field")
        if hash.digest <= field.extension_degree:
            raise StarkError("Provided hash has too short output")

        self.field = field
        self.seed = seed.encode()
        self.base_hash = base_hash
        self.counter = 0

    def _bitstream_iter(self, hexstring):
        i = 0
        while i < self.field.extension_degree:
            yield (hexstring[i / 8] a >> (i % 8)) & 1
            i += 1
        return None

    def __call__():
        digest = base_hash(struct.pack(">q", self.counter) + self.seed)
        self.counter += 1
        return self.field([x for x in self._bitstream_iter(digest)])