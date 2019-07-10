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
        f_commitment = self.merkleTreeFactory([f.evaluate(x) for x in self.D1])
        alpha = self.field.from_hash(f_commitment.get_merkle_root())
        constraints = len(self.ARP_instance.C)
        alpha_powes = [alpha**(i+1) for xrange(constraints)]

        g = 0
        for coeff, M, P, Q in zip(alpha_powers, constraints):
            elems = [f.substitute(m * self.X) for  m in M]
            g += coeff * P.substitute(elems) / Q

        g_commitment = self.merkleTreeFactory([g.evaluate(x) for x in self.D2])        
        z = self.field.from_hash(g_commitment.get_merkle_root())
        while z in self.D2:
            z += 1

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

        prox_proof_h1 = self.ProximityProver(self.D1, self.merkleTreeFactory).generate_proof(h1)
        prox_proof_h2 = self.ProximityProver(self.D2, self.merkleTreeFactory).generate_proof(h2)

        #now check that oracles for h1 and h2 agree with corresponding oracles for f and g
        cor_queries = []
        for domain, proximity_proof, commitment in [(self.D1, prox_proof_h1, f_commitment), (self.D2, prox_proof_h2, g_commitment)]:
            root_hashes, f_last_coeffs, query_proof = proximity_proof
            coeffs_tree = self.merkleTreeFactory(coeffs)
            s = domain.from_hash(coeffs_tree.get_merkle_root())
       
            coset_indices = [domain.get_index(p, 0) for p in domain.get_coset(s, 0)]
            cor_queries.append((commitments[i].get_leaf(idx), commitments[i].get_proof(idx)) for idx in coset_indices)
        
        ALI_proof = (f_commitment.get_merkle_root(), g_commitment.get_merkle_root(), a_arr, prox_proof_h1, prox_proof_h2, cor_queries)
        return ALI_proof

    #h * B = (f - A)
    def _check_poly_correspondence(self, domain, h_proximity_proof, f_queries, f_commitment_root, A, B):
        h_last_coeffs = proximity_proof[1]
        h_queries = h_proximity_proof[2][0]
        coeffs_tree = self.merkleTreeFactory(coeffs)
        s = domain.from_hash(coeffs_tree.get_merkle_root())

        coset = domain.get_coset(s, 0)
        coset_indices = [domain.get_index(p, 0) for p in coset]

        for idx, x, (f_leaf, f_proof), (g_leaf, g_proof) in zip(coset_indices, coset, f_queries, h_queries):
            if not self.merkleTreeFactory.validate_proof(f_leaf, idx, f_proof, f_commitment_root):
                    return False

            import copy
            A_copy = copy.deepcopy(A)
            B_copy = copy.deepcopy(B)
            
            if h_leaf * B_copy(x) != f_leaf - A_copy():
                return False
        return True


    def validate_proof(self, ALI_proof):
        f_commitment_root, g_commitment_root, a_arr, prox_proof_h1, prox_proof_h2, cor_queries = ALI_proof
        constraints = len(self.ARP_instance.C)

        check_prox_proof_h1 = self.ProximityProver(self.D1, self.merkleTreeFactory).validate_proof(prox_proof_h1)
        check_prox_proof_h2 = self.ProximityProver(self.D2, self.merkleTreeFactory).validate_proof(prox_proof_h2)
        if not check_prox_proof_h1 or not check_prox_proof_h2:
            return False

        alpha = self.field.from_hash(f_commitment_root]
        alpha_powes = [alpha**(i+1) for xrange(constraints)]
        z = self.field.from_hash(g_commitment_root)
        while z in self.D2:
            z += 1

        M_z = [z * m for m in self._get_full_mask_iter(m)]
        Z = reduce((lambda x, y: x * (self.X - y), M_z, 1))
        U = construct_interpolation_poly(self.poly_ring, M_z, a_arr)

        if not self._check_poly_correspondence(self.D1, prox_proof_h1, cor_queries[0], f_commitment_root, U, Z):
            return False

        #verifier computes the alleged value of b, using provided a_arr
        b = 0
        i = 0
        for coeff, M, P, Q in zip(alpha_powers, constraints):
            import copy
            P_copy = copy.deepcopy(P)
            Q_copy = copy.deepcopy(Q)

            var_count = P.get_num_of_vars()
            b += coeff * P_copy.evaluate(a_arr[i:i+var_count]) / Q_copy.evaluate(z) 
            i+=var_count

        #TODO: we need to use PolyProxy here because we are now unable to interpret b as a polynomial function
        b = PolyProxy(self.poly_ring, {self.field(0): b})
        if not self._check_poly_correspondence(self.D2, prox_proof_h2, cor_queries[1], g_commitment_root, b, self.X - z):
            return False
        return True

        

        

        