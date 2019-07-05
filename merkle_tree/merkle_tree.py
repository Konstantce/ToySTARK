from poseidon_hash import PoseidonHash

from utils import utils

import hashlib #we may use hashlib.sha256
import binascii
import itertools
from math import log


@utils.memoize
def MerkleTreeFactory(hash_function = PoseidonHash, descendant_count = 4, leaf_encoder = binascii.unhexlify, padding = None):

    def grouper(iterable, n):
        it = iter(iterable)
        while True:
            chunk = tuple(itertools.islice(it, n))
            if not chunk:
                return
            yield chunk

    def raw2hex(x):
        return binascii.hexlify(x)

    def hex2row(x):
        return binascii.unhexlify(x)
    
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
                raise utils.StarkError("Impossible to construct Merkle tree: number of leaves is not a power of descendant_count")

            for v in values:
                self.leaves.append(v)
                if self.leaf_encoder:
                    self.encoded_leaves.append(leaf_encoder(v))

            if self.padding is not None:
                self.leaves += [self.padding] * (padded_list_count - len(self.leaves))
                if self.leaf_encoder:
                    print (padded_list_count - len(self.encoded_leaves))
                    self.encoded_leaves += [leaf_encoder(self.padding)] * (padded_list_count - len(self.encoded_leaves)) 

        @classmethod
        def _get_padded_leaves_count(cls, num):
            n = int(log(num, cls.descendant_count))
            probe = cls.descendant_count ** n
            return probe if probe == num else probe * cls.descendant_count
            
        def get_leaf(self, index):
            return self.leaves[index]

        def get_leaf_count(self):
            return len(self.leaves)

        def __calculate_next_level(self):
            N = len(self.levels[0])  # number of leaves on the level
            if N % self.descendant_count != 0:
                raise utils.StarkError("Unexpected error in Merkle tree construction")
                
            new_level = []
            for elems in grouper(self.levels[0], self.descendant_count):
                new_level.append(self.hash_function(''.join(elems)).digest())
            self.levels = [new_level, ] + self.levels  # prepend new level

        def __make_tree(self):
            self.__is_ready = False
            if self.get_leaf_count() > 0:
                self.levels = [self.encoded_leaves, ]
                while len(self.levels[0]) > 1:
                    self.__calculate_next_level()
            self.__is_ready = True

        def get_merkle_root(self):
            if self.__is_ready:
                if self.levels is not None:
                    return raw2hex(self.levels[0][0])
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
                raise utils.StarkError("Provided index is out of range.")
            else:
                init_index = index
                proof = []
                for level in range(len(self.levels) - 1, 0, -1):
                    x = index % self.descendant_count

                    start_pos = index - x
                    node_pos = start_pos + x
                    end_pos = start_pos + self.descendant_count
                    subproof = []

                    for cur_pos in xrange(start_pos, end_pos): 
                        if cur_pos == node_pos:
                            subproof.append(utils.p_)
                        else:
                            subproof.append(raw2hex(self.levels[level][cur_pos]))
                    
                    proof.append(subproof)
                    index = int(index / self.descendant_count)

                root = self.get_merkle_root()
                print proof
                assert self.validate_proof(self.leaves[init_index], init_index, proof, root), "Constructed merkle proof is incorrect!"
                return proof

        @classmethod
        def validate_proof(cls, leaf, index, proof, merkle_root):
            target_hash = cls.leaf_encoder(leaf) if cls.leaf_encoder else leaf
            merkle_root = hex2row(merkle_root)

            if len(proof) == 0:
                return target_hash == merkle_root
            else:
                running_hash = target_hash
                for subproof in proof:
                    if not isinstance(subproof[index % cls.descendant_count], utils.Placeholder):
                        print "Here!"
                        return False
                    index /= cls.descendant_count
                    
                    data = b"".join([hex2row(x) if not isinstance(x, utils.Placeholder) else running_hash for x in subproof])
                    running_hash = cls.hash_function(data).digest()
                return running_hash == merkle_root


    MerkleTree.hash_function = hash_function
    MerkleTree.descendant_count = descendant_count 
    MerkleTree.leaf_encoder = leaf_encoder 
    MerkleTree.padding = padding

    return MerkleTree