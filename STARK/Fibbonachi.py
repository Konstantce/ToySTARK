import sys
from os import path
sys.path.append( path.dirname( path.dirname( path.abspath(__file__) ) ) )


from algebra.finite_field import *

p = 17
Fp = IntegersModP(p, 3)

#import merklee tree
from merkle_tree.merkle_tree import *

def residue_field_hasher(x):
    x = hex(int(x))
    if x[-1] == "L":
        x = x[:-1]
    if len(x) % 2 !=0:
        x = "0" + x
    return x


tree_constructor = MerkleTreeFactory(leaf_encoder = residue_field_hasher, padding = Fp(0))

from FRI.domain_ierarchy import *
from FRI.fri_opp import *

domain_ierarchy = MultiplicativeDomainIerarchy(Fp, 16, 5, 1)
fri = FRI_OPP(domain_ierarchy, tree_constructor)

from algebra.polynomials import *

poly_ring = multiivar_polynomialsOver(Fp, 'X')

f = poly_ring.from_string("X**2")

proof = fri.generate_proof(f)
print fri.validate_proof(proof)





