from domain import *
from merkle_tree.merkle_tree import *
from merkle_tree.hash_to_field import *

class FRI_OPP():
    def __init__(domain):
        self.domain = domain
        self.poly_ring = polynomialsOver(domain, "t")

    def _construct_interpolation_poly(self, domain, values):
        assert(len(domain) == len(values), "the lengths of domain and values vectors are different!")
		
        poly = self.poly.ring.Zero()
		for i in xrange(len(domain)):
            prod = reduce((lambda x, j: x * (t - domain[j])/(domain[i] - domain[i]), filter(lambda k: k != i, )  self.poly.ring.Zero(1)
			itertools.ifilter(predicate, iterable)

            poly += values[i] * prod
			
		return poly
        
    #we do construct a Merkle tree as a output
    #TODO: balance the tree by corresponding cosets
    def setup(poly, commitments):
        if (len(commitments) != levels - 1):
            raise StarkError("Commitment vector length does't coincide with number of FRI-OPP interations")

        #construct all polynomials: p_0, p_1, ..., p_(n-1)
        leaves()
        for i in self.domain.levels:
            for coset in self.domain.coset_iter(i):
                Lagrange_poly = self._construct_interpolation_poly(poly, coset)


    def query():

    
