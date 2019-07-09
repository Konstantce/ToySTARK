from algebra.polynomials import *
from utils.utils import *

import itertools

class ARP:
    def __init__(self, instance, witness = None):
        """Instance format: The instance x is a tuple (Fq, d, C) where:
            * Fq is a finite field of size q.
            * d is an integer representing a bound on the degree of the witness.
            * C is a set of |C| tuples (M_i, P_i, Q_i) representing constraints, where 
                M_i is the mask which is a sequence of field elements M_i = {M_ij in Fq} for j in (1..|M_i|)
                P_i is the condition of the constraint which is a polynomial with |Mi| variables. 
                Q_i in Fq[x] is the domain polynomial of the constraint which should vanish on the locations where the constraint should hold.
                (here we represent Q_i as a set of its' roots)
        """

        (field, d, C) = instance
        self.field = field
        self.degree = d
        self.constraints = C        

        """Witness format: The witness w is a polynomial f in Fq[x]. A constraint (M, P, Q) is said to hold at a location x in Fq 
           if P(f(x * M_1), f(x * M_2), ..., f(x * M_|M|)) = 0
           We say that f satisfies the constraint if previous equality holds at every x in Fq for which Q(x) = 0.
           We say that w satisfies the instance if and only if deg(f) < d and f satisfies all of the
           constraints. 
        """
        self.witness = witness

    def check_witness(self):
        assert self.witness is not None, "Witness is undefined at this point."
        #copy witness for now
        import copy
        witness = copy.deepcopy(self.witness)

        if witness.degree() > self.degree:
            return False
        for M, P, Q in self.constraints:
            for x in Q:
                if P.evaluate([witness.evaluate(x*m) for m in M]) != 0:
                    return False

        return True

    def set_witness(self, witness):
        self.witness = witness

    @classmethod
    def fromAIR(cls, AIR):
        assert AIR.consistency_check(), "AIR instance is not fully defined."
        field = AIR.field
        W = AIR.w
        T = AIR.T
        poly_ring = polynomialsOver(field, "X")

        mul_group_order = field.get_num_of_elems() - 1
        if mul_group_order % (W*T) != 0:
            raise StarkError("Unable to generate ARP instance for %s of size %d" %(field, W*T))

        gamma = field.get_prim_element() ** (mul_group_order / (W*T))
        full_mask = [gamma ** k for k in xrange(2*W)]
        Q = [gamma ** (W*k) for k in xrange(T)]
        C = [(full_mask, P, Q) for P in AIR.trace_constraints]
        C += [([1], X - alpha, [gamma**(i*W+j)]) for (i, j, alpha) in AIR.boundary_constraints]

        #TODO: how is degree defined?
        degree = T * W
        instance = (field, degree, C)

        if AIR.witness is not None:
            domain, values = zip(*[(gamma**(t*W+j), AIR.witness[t][j]) for  (t, j) in itertools.product(xrange(T), xrange(W))])
            witness = construct_interpolation_poly(poly_ring, domain, values)
        else:
            witness = None

        return cls(instance, witness)
        