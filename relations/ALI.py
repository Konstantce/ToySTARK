from algebra.polynomials import *

#we actuall implement DEEP version of ALI here
#we do-not implement zk

class ALI:
    #here D1 and D2 should be FRI-OPP domains
    def __init__(self, ARP_instance, D1, D1, merkleTreeFactory, ProximityProver):
        self.ARP_instance = ARP_instance
        self.D1 = D1
        self.D2 = D2
        self.field = ARP_instance.field
        self.merkleTreeFactory = merkleTreeFactory
        self.ProximityProver = ProximityProver

        self.poly_ring = polynomialsOver(self.field, "X")
        self.X = self.poly_ring([0, 1])

    def _get_full_mask_iter(self):
        for M, P, Q in self.constraints:
            for m in M:
                yield m
        return 

    def generate_proof(self, f):
        f_commitment = self.merkleTreeFactory([f.evaluate(x) for x in D1])
        alpha = self.field.from_hash(f_commitment.get_merkle_root())
        constraints = len(self.ARP_instance.C)
        alpha_powes = [alpha**(i+1) for xrange(constraints)]

        g = 0
        for coeff, M, P, Q in zip(alpha_powers, constraints):
            elems = [f.substitute(m * self.X) for  m in M]
            g += coeff * P.substitute(elems) / Q

        g_commitment = self.merkleTreeFactory([g.evaluate(x) for x in D2])        
        z = self.field.from_hash(g_commitment.get_merkle_root())
        while z in D2:
            z+=1

        M_z = [z * m for m in self._get_full_mask_iter(m)]
        a_arr = []
        for x in M_z:
            import copy
            f_copy = copy.deepcopy(f)
            a_arr.append(f_copy.evaluate(x))

        #construct U and G and send them
        Z = reduce((lambda x, y: x * (self.X - y), M_z, 1))
        U = construct_interpolation_poly(self.poly_ring, M_z, a_arr)

        h1 = (f - U)/Z
        g_copy = copy.deepcopy(g)
        h2 = (g - g.evaluate(z))/(self.X - z)
        prox_proof_h1 = self.ProximityProver(h1)
        prox_proof_h2 = self.ProximityProver(h2)

        #and check that oracles the agree - work only with FRI-OPP protocol for now


    def validate_proof(self, proof):
        return self
        