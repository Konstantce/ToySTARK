from algebra.polynomials import *

#we actuall implement DEEP version of ALI here
#we do-not implement zk

class ALI:
    #here D1 and D2 should be FRI-OPP domains
    def __init__(self, ARP_instance, D1, D2, merkleTreeFactory, ProximityProver):
        print "size: ", ARP_instance.size
        print "domain size: ", D1.get_size()
        assert ARP_instance.size == D1.get_size(), "unable to place ARP inside AIR"

        self.ARP_instance = ARP_instance
        self.D1 = D1
        self.D2 = D2
        self.field = ARP_instance.field
        self.merkleTreeFactory = merkleTreeFactory
        self.ProximityProver = ProximityProver

        self.poly_ring = polynomialsOver(self.field, "X")
        self.X = self.poly_ring([0, 1])

    def _get_full_mask_iter(self):
        for M, _, _ in self.ARP_instance.constraints:
            for m in M:
                yield m
        return

    def _construct_Q_poly(self, Q):
        return reduce((lambda x, y: x * (self.X - y)), Q, 1) 

    def generate_proof(self, f):
        f_commitment = self.merkleTreeFactory([f.evaluate(x) for x in self.D1])
        alpha = self.field.from_hash(f_commitment.get_merkle_root())
        len_constraints = len(self.ARP_instance.constraints)
        alpha_powers = [alpha**(i+1) for i in xrange(len_constraints)]

        g = 0
        for coeff, (M, P, Q) in zip(alpha_powers, self.ARP_instance.constraints):
            elems = [f.substitute([m * self.X]) for  m in M]
            g += coeff * P.substitute(elems) / self._construct_Q_poly(Q)

        g_commitment = self.merkleTreeFactory([g.evaluate(x) for x in self.D2])        
        z = self.field.from_hash(g_commitment.get_merkle_root())
        while z in self.D2:
            z += 1

        M_z_dict = dict.fromkeys([z * m for m in self._get_full_mask_iter()])
        for x in M_z_dict:
            import copy
            f_copy = copy.deepcopy(f)
            M_z_dict[x] = f_copy.evaluate(x)

        #construct U and G and send them
        Z = reduce((lambda x, y: x * (self.X - y)), M_z_dict.keys(), 1)
        domain, values = zip(*M_z_dict.items())
        U = construct_interpolation_poly(self.poly_ring, domain, values)

        h1 = (f - U)/Z
        g_copy = copy.deepcopy(g)
        h2 = (g - g_copy.evaluate(z))/(self.X - z)

        prox_proof_h1 = self.ProximityProver(self.D1, self.merkleTreeFactory).generate_proof(h1)
        prox_proof_h2 = self.ProximityProver(self.D2, self.merkleTreeFactory).generate_proof(h2)

        #now check that oracles for h1 and h2 agree with corresponding oracles for f and g
        cor_queries = []
        for domain, proximity_proof, commitment in [(self.D1, prox_proof_h1, f_commitment), (self.D2, prox_proof_h2, g_commitment)]:
            
            coeffs_tree = self.merkleTreeFactory(proximity_proof[0][1])
            s = domain.from_hash(coeffs_tree.get_merkle_root())
       
            coset_indices = [domain.get_index(p, 0) for p in domain.get_coset(s, 0)]
            cor_queries.append([(commitment.get_leaf(idx), commitment.get_proof(idx)) for idx in coset_indices])
        
        ALI_proof = (f_commitment.get_merkle_root(), g_commitment.get_merkle_root(), M_z_dict, prox_proof_h1, prox_proof_h2, cor_queries)
        return ALI_proof

    #h * B = (f - A)
    def _check_poly_correspondence(self, domain, h_proximity_proof, f_queries, f_commitment_root, A, B):
        h_last_coeffs = h_proximity_proof[0][1]
        h_queries = h_proximity_proof[1][0]
        coeffs_tree = self.merkleTreeFactory(h_last_coeffs)
        s = domain.from_hash(coeffs_tree.get_merkle_root())

        coset = domain.get_coset(s, 0)
        coset_indices = [domain.get_index(p, 0) for p in coset]

        for idx, x, (f_leaf, f_proof), (h_leaf, _) in zip(coset_indices, coset, f_queries, h_queries):
            if not self.merkleTreeFactory.validate_proof(f_leaf, idx, f_proof, f_commitment_root):
                    return False

            import copy
            A_copy = copy.deepcopy(A)
            B_copy = copy.deepcopy(B)
            x = x[0]
            if h_leaf * B_copy(x) != f_leaf - A_copy(x):
                return False
        return True


    def validate_proof(self, ALI_proof):
        f_commitment_root, g_commitment_root, M_z_dict, prox_proof_h1, prox_proof_h2, cor_queries = ALI_proof
        len_constraints = len(self.ARP_instance.constraints)

        check_prox_proof_h1 = self.ProximityProver(self.D1, self.merkleTreeFactory).validate_proof(prox_proof_h1)
        check_prox_proof_h2 = self.ProximityProver(self.D2, self.merkleTreeFactory).validate_proof(prox_proof_h2)
        if not check_prox_proof_h1 or not check_prox_proof_h2:
            return False

        alpha = self.field.from_hash(f_commitment_root)
        alpha_powers = [alpha**(i+1) for i in xrange(len_constraints)]
        z = self.field.from_hash(g_commitment_root)
        while z in self.D2:
            z += 1

        Z = reduce((lambda x, y: x * (self.X - y)), M_z_dict.keys(), 1)
        domain, values = zip(*M_z_dict.items())
        U = construct_interpolation_poly(self.poly_ring, domain, values)

        if not self._check_poly_correspondence(self.D1, prox_proof_h1, cor_queries[0], f_commitment_root, U, Z):
            return False

        #verifier computes the alleged value of b, using provided a_arr
        b = 0
        for coeff, (M, P, Q) in zip(alpha_powers, self.ARP_instance.constraints):
            import copy
            P_copy = copy.deepcopy(P)
            Q_copy = self._construct_Q_poly(Q)
            b += coeff * P_copy.evaluate([M_z_dict[z * m] for m in M]) / Q_copy.evaluate(z) 

        #TODO: we need to use PolyProxy here because we are now unable to interpret b as a polynomial function
        b = PolyProxy(self.poly_ring, {self.field(0): b})
        if not self._check_poly_correspondence(self.D2, prox_proof_h2, cor_queries[1], g_commitment_root, b, self.X - z):
            return False
        return True

        

        

        