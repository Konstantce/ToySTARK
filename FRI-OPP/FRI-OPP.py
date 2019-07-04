from domain_ierarchy import *
from merkle_tree.merkle_tree import *
from utils.utils import *
from UnivariatePolynomialProxy.poly_proxy import *

import itertools

class FRI_OPP():
    def __init__(domain_ierarchy, merkle_tree):
        self.domain_ierarchy = domain_ierarchy
        self.field = domain_ierarchy.get_field()
        self.poly_ring = polynomialsOver(field, "t")
        self.merkle_tree = merkle_tree

    #TODO: balance the tree by corresponding cosets
    def generate_proof(self, poly):
        #emulate commit phase
        #construct all polynomials: f_0, f_1, ..., f_(n-1)

        f_commitments = []
        f = poly

        for i in xrange(self.domain_ierarchy.levels - 1):
            #commit to current f-poly
            leaves = [f(x) for x  in self.domain_ierarchy.get_domain_iter(i)]
            tree = self.merkle_tree(leaves)
            f_commitments.append(tree)
            sample_point = self.field.from_hash(tree.get_merkle_root())

            #construct next polynomial
            f_new = {}
            for coset in self.domain_ierarchy.get_coset_iter(i):
                values = [f(x) for x in coset]
                Lagrange_poly = construct_interpolation_poly(self.field, coset, values)
                y = self.domain.map_to_subdomain(coset[0], i)
                f_new[y] = Lagrange_poly.evaluate(sample_point)
            f = PolyProxy(f_new)

    #for final step - just return the coefficients of the last polynomial f_n
    coeffs = f.get_coefficients()
    commitment_proof = ([tree.get_merkle_root() for tree in f_commitment], coeffs)

    #from now emulate query phase
    coeffs_tree = self.merkle_tree(coeffs)
    s = self.domain_ierarchy.from_hash(coeffs_tree.get_merkle_root())
    query_proof = []

    for i in self.domain_ierarchy.levels:
        coset_indices = [self.domain_ierarchy.get_index(p, i) for p self.domain.get_coset(s, i)]
        level_query = [(f_commitment[i].get_leaf(idx), f_commitment[i].get_proof(idx)) for idx in coset_indices)]
        query_proof.append(level_query)
        s = self.domain_ierarchy.map_to_subdomain(s)

    return (commitment_proof, query_proof)


    def validate_proof(self, proof):
        commitment_proof, query_proof = proof
        root_hashes, f_last_coeffs = commitment_proof

        coeffs_tree = self.merkle_tree(f_last_coeffs)
        s = self.domain_ierarchy.from_hash(coeffs_tree.get_merkle_root())

        for i in xrange(self.domain_ierarchy.levels - 1):
            coset = self.domain_ierarchy.get_coset(s, i)
            coset_indices = [self.domain_ierarchy.get_index(p, i) for p in coset]
            for idx, (leaf, proof) in zip(coset_indices, query_proof[i]):
                if not self.merkle_tree.validate_proof(leaf, idx, proof, root_hashes[i]):
                    return False

            #perform ’round consistency’ check
            interpolant = construct_interpolation_poly(field, coset, [x for (x, y) in query_proof[i]])
            sample_point = self.field.from_hash(root_hashes[i])

            if i != self.domain_ierarchy.levels - 2:
                y, _ = query_proof[i+1][0]              
            else:
                #last round
                f_last = self.poly_ring(f_last_coeffs)
                s = self.domain_ierarchy.map_to_subdomain(s, i)
                y = f_last.evaluate(s)

            if  y != interpolant.evaluate(sample_point):
                    return False
        
        return True




    
