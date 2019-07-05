import sys
from os import path
sys.path.append( path.dirname( path.dirname( path.abspath(__file__) ) ) )

import parameters as parameters
from utils.utils import *
from merkle_tree.merkle_tree import *

import itertools

a = [1, 2, 3, 4, 5, 6]

def grouper(n, iterable):
    it = iter(iterable)
    while True:
       chunk = tuple(itertools.islice(it, n))
       if not chunk:
           return
       yield chunk

for elems in grouper(4, iter(a)):
    print elems

merkle_tree = MerkleTreeFactory()
tree = merkle_tree(["deadbeef", "11234561"])
tree.get_proof(0)

from binascii import unhexlify
b = unhexlify("deadbeef")
print b