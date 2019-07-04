from domain import *
from merkle_tree.merkle_tree import *
from merkle_tree.hasher_to_field import *
import itertools

class FRI_OPP():
    def __init__(domain, merkleTreeFactory, hasher_to_field):
        self.domain = domain
        self.poly_ring = polynomialsOver(domain, "t")
        self.merkleTreeFactory = merkleTreeFactory
        self.hasher_to_field = hasher_to_field

    
        
    #we do construct Merkle trees as a output
    #TODO: balance the tree by corresponding cosets
    #NB: poly is represented in the form of domain
    def generate_proof(self, poly):
        #emulate commit phase

        #construct all polynomials: f_0, f_1, ..., f_(n-1)
        f_commitments = []
        f = poly

        for i in self.domain.levels:
            #commit to current f-poly
            leaves = []
            for coset in self.domain.coset_iter(i):
                leaves += [f[x] for x in coset]
                tree = self.merkleTreeFactory(leaves)
                f_commitments.append(tree)
                commitment = self.hasher_to_field(tree.get_merkle_root())

            #construct nex polynomial
            f_new = {}
            for coset in self.domain.coset_iter(i):
                values = [f[x] for x in coset]
                Lagrange_poly = self._construct_interpolation_poly(coset, values)
                y = self.domain.map_to_subdomain(coset[0])
                f_new[y] = Lagrange_poly.evaluate(commitment)
            f = f_new

    #for final step - just return the coefficients of the last polynomial f_n
    domain, values = zip(*f.items())
    f_last = self._construct_interpolation_poly(domain, values)
    coeffs = f_last.coefficients
    commitment_proof = ([tree.get_merkle_root() for tree in f_commitment], coeffs)

    #from now emulate query phase
    coeffs_tree = self.MerkleTreeFactory(coeffs)
    s = self.domain.get_elem_from_random_bytes(coeffs_tree.get_merkle_root())
    query_proof = []

    for i in self.domain.levels:
        coset_idx = self.domain.get_coset_index(s, i)
        coset_size = self.domain.get_coset_size(i)
        level_query = [(f_commitment[i].get_leaf(idx), f_commitment[i].get_proof(idx)) for idx in xrange(coset_idx, coset_idx + coset_size)]
        query_proof.append(level_query)
        s = self.domain.map_to_subdomain(s)

    return (commitment_proof, query_proof)

    def validate_proof(self, proof):
        commitment_proof, query_proof = proof
        root_hashes, coeffs = commitment_proof

        coeffs_tree = self.MerkleTreeFactory(coeffs)
        s = self.domain.get_elem_from_random_bytes(coeffs_tree.get_merkle_root())

        for i in self.domain.levels:
            coset_idx = self.domain.get_coset_index(s, i)
            coset_size = self.domain.get_coset_size(i)
            coset = self.domain.get_coset(coset_idx)
            idx = coset_idx
            for (leaf, proof) in query_proof[i]:
                if not self.MerkleTreeFactory.validate_proof(proof, leaf, root_hashes[i]):
                    return False
            interpolant = self._construct_interpolation_poly(coset, leaves)
            #TODO: apply round consistency check here




    
