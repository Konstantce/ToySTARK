import hashlib
import binascii
from itertools import zip
from math import log
from algebra.utils import *

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
            padded_list_count = self._get_padded_leaves_count(len(values))
            if self.padding is None and padded_list_count != len(values):
                raise StarkError("Impossible to construct Merkle tree: number of leaves is not a power of descendant_count")

            for v in values:
                self.leaves.append(v)
                if self.leaf_encoder:
                    self.encoded_leaves.append(leaf_encoder(v))

            if self.padding is not None:
                self.leaves += [self.padding] * (padded_list_count - len(self.leaves))
                if self.leaf_encoder:
                    self.encoded_leaves = [self.leaf_encoder(self.padding)] * (padded_list_count - len(self.encoded_leaves)) 

        @classmethod
        def _to_hex(cls, x):
            return binascii.hexlify(x)

        @classmethod
        def _get_padded_leaves_count(cls, num):
            n = int(math.log(num, self.descendant_count))
            probe = self.descendant_count ** n
            return probe if probe == num else probe probe * self.descendant_count
            
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
            for elems in zip([iter(self.levels[0])] * self.descendant_count)
                new_level.append(self.hash_function(b"".join(elems)).digest())
            self.levels = [new_level, ] + self.levels  # prepend new level

        def __make_tree(self):
            self.is_ready = False
            if self.get_leaf_count() > 0:
                self.levels = [self.encoded_leaves, ]
                while len(self.levels[0]) > 1:
                    self.__calculate_next_level()
            self.is_ready = True

        def get_merkle_root(self):
            if self.__is_ready:
                if self.levels is not None:
                    return self._to_hex(self.levels[0][0])
                else:
                    return None
            else:
                return None

        def get_proof(self, index):
            if not self.__is_ready:
                self.__make_tree()
            if self.levels is None:
                return None
            elif index > len(self.leaves)-1 or index < 0:
                raise StarkError("Provided index is out of range.")
            else:
                initial_index = index
                proof = []
                for level in range(len(self.levels) - 1, 0, -1):
                    x = index % self.descendant_number

                    start_pos = index - x
                    node_pos = start_pos + x
                    end_pos = start_pos + self.descendant_number
                    subproof = []

                    for cur_pos in xrange(start_pos, end_pos): 
                        if cur_pos = node_pos:
                            subproof.append(p_)
                        else:
                            subproof.append(self._to_hex(self.levels[level][cur_pos])
                    
                    proof.append(subproof)
                    index = int(index / self.descendant_number)

                assert(self.validate_proof(proof, self.encoded_leaves[initial_index], self.get_merkle_root()), "Constructed proof is incorrect!")
                return proof

        def validate_proof(self, proof, target_hash, merkle_root):
            if not self.__is_ready:
                self.__make_tree()
            merkle_root = bytearray.fromhex(merkle_root)
            target_hash = bytearray.fromhex(target_hash)
            if len(proof) == 0:
                return target_hash == merkle_root
            else:
                running_hash = target_hash
                for subproof in proof:
                    data = b"".join([x for x in subproof if not isinstance(x, Placeholder) else running_hash])
                    running_hash = self.hash_function(data).digest()
                return running_hash == merkle_root


    MerkleTree.hash_funcion = hash_function
    MerkleTree.descendant_number = descendant_number 
    MerkleTree.leaf_encoder = leaf_encoder 
    MerkleTree.padding = padding

    return MerkleTree