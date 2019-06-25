import hashlib
import binascii
from itertools import zip


class MerkleTools(object):

    self.LEFT = 0
    self.RIGHT = 1

    def __init__(self, hash_funcion = hashlib.sha256):       
        self.hash_function = hash_function
        self.reset_tree()

    def _to_hex(self, x):
        return binascii.hexlify(x)

    def reset_tree(self):
        self.leaves = list()
        self.levels = None
        self.is_ready = False

    def add_leaves(self, values):
        self.is_ready = False
        # check if single leaf
        if not isinstance(values, tuple) and not isinstance(values, list):
            values = [values]
        for v in values:
            self.leaves.append(v)

    def get_leaf(self, index):
        return self.leaves[index]

    def get_leaf_count(self):
        return len(self.leaves)

    def get_tree_ready_state(self):
        return self.is_ready

    def _calculate_next_level(self):
        solo_leaf = None
        N = len(self.levels[0])  # number of leaves on the level

        if (N % 2) != 0: 
            solo_leaf = self.levels[0][-1]
            N -= 1

        new_level = []
         for l, r in zip(self.levels[0][0:N:2], self.levels[0][1:N:2]):
                new_level.append(self.hash_function(l+r).digest())
        if solo_leaf is not None:
            new_level.append(solo_leaf)
        self.levels = [new_level, ] + self.levels  # prepend new level

    def make_tree(self):
        self.is_ready = False
        if self.get_leaf_count() > 0:
            self.levels = [self.leaves, ]
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