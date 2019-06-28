import hashlib
import binascii
from itertools import zip
from math import log
from algebra.utils import memoize

@memoize
def MerkleTreeFactory(hash_funcion = hashlib.sha256, descendant_count = 2, leaf_encoder = None, padding = None):

    class MerkleTree():
        def __init__(self, values):
            self.__is_ready = False
            self.leaves = list()
            self.encoded_leaves = list() if self.leaf_encoder else self.leaves
            self.levels = None
            # check if single leaf
            if not isinstance(values, tuple) and not isinstance(values, list):
                values = [values]
            if self.padding is None and not self._check_num_of_leaves(len(values)):
                raise StarkError("Impossible to construct Merkle tree: number of leaves is not a power of descendant_count")

            for v in values:
                self.leaves.append(v)
                if self.leaf_encoder:
                    self.encoded_levels.append(leaf_encoder(v))

        @classmethod
        def _to_hex(cls, x):
            return binascii.hexlify(x)

        @classmethod
        def _check_num_of_leaves(cls, num):
            n = int(math.log(num, self.descendant_count))
            return self.descendant_count ** n == num
            
        def get_leaf(self, index):
            return self.leaves[index]

        def get_leaf_count(self):
            return len(self.leaves)

        def __calculate_next_level(self):
            solo_leaves = None
            N = len(self.levels[0])  # number of leaves on the level
            if N % self.descendant_count != 0:
                raise StarkError("Unexpected error in Merkle tree construction")
                
            new_level = []
            zip([iter(self.levels[0]) * self.s])
            for l, r in zip(self.levels[0][0:N:2], self.levels[0][1:N:2]):
                    new_level.append(self.hash_function(l+r).digest())
            if solo_leaf is not None:
                new_level.append(solo_leaf)
            self.levels = [new_level, ] + self.levels  # prepend new level

        def __make_tree(self):
            self.is_ready = False
            if self.get_leaf_count() > 0:
                self.levels = [self.encoded_leaves, ]
                while len(self.levels[0]) > 1:
                    self._calculate_next_level()
            self.is_ready = True

        def get_merkle_root(self):
            if self.is_ready:
                if self.levels is not None:
                    return self._to_hex(self.levels[0][0])
                else:
                    return None
            else:
                return None

        def get_proof(self, index):
            if self.levels is None:
                return None
            elif not self.is_ready or index > len(self.leaves)-1 or index < 0:
                return None
            else:
                proof = []
                for x in range(len(self.levels) - 1, 0, -1):
                    level_len = len(self.levels[x])
                    if (index == level_len - 1) and (level_len % 2 == 1):  # skip if this is an odd end node
                        index = int(index / 2.)
                        continue
                    is_right_node = index % 2
                    sibling_index = index - 1 if is_right_node else index + 1
                    sibling_pos = self.LEFT if is_right_node else self.RIGHT
                    sibling_value = self._to_hex(self.levels[x][sibling_index])
                    proof.append((sibling_pos, sibling_value))
                    index = int(index / 2.)
                return proof

        def validate_proof(self, proof, target_hash, merkle_root):
            merkle_root = bytearray.fromhex(merkle_root)
            target_hash = bytearray.fromhex(target_hash)
            if len(proof) == 0:
                return target_hash == merkle_root
            else:
                proof_hash = target_hash
                for sibling, proof_hash in proof:
                    data = sibling + proof_hash if sibling == self.LEFT else proof_hash + sibling
                    proof_hash = self.hash_function(data).digest()
                return proof_hash == merkle_root


    hash_funcion = hashlib.sha256, descendant_number = 2, leaf_encoder = None, padding = None
    Fq.__name__ = 'F_{%d^%d}' % (p,m)
   Fq.prim_elem = None
   Fq.is_extension_field = True
   return Fq