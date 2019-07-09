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

from relations import AIR

num_registers = 2
num_steps = 4
air = AIR.AIR(num_registers, num_steps, Fp)
air.add_boundary_constraint(0, 0, Fp(1))
air.add_boundary_constraint(0, 1, Fp(1))
air.add_boundary_constraint(3, 1, Fp(5))
witness = [
    [Fp(1), Fp(1)],
    [Fp(1), Fp(2)],
    [Fp(2), Fp(3)],
    [Fp(3), Fp(5)],
]
c0 = air.poly_ring.from_string("0*Y2 + Y1 - X2")
c1 = air.poly_ring.from_string("Y2 - X1 - X2")

air.add_trace_constraint(c0)
air.add_trace_constraint(c1)
air.set_circuit((lambda x, y: x & y))

air.set_witness(witness)
print air.consistency_check()

from relations.ARP import *

arp = ARP.fromAIR(air)
print arp.check_witness()

g = poly_ring.from_string("X+1")


mult_var_poly = multiivar_polynomialsOver(Fp, "X", "Y", "Z")

h = mult_var_poly.from_string("X*Y + Z")
print h.substitute([f, g, f])







