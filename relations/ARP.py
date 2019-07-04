import itertools

class APR:
    def __init__(self, istance, witness = None):
        """Instance format: The instance x is a tuple (Fq, d, C) where:
            • Fq is a finite field of size q.
            • d is an integer representing a bound on the degree of the witness.
            • C is a set of |C| tuples (M_i, P_i, Q_i) representing constraints, where 
                M_i is the mask which is a sequence of field elements M_i = {M_ij ∈ Fq} for j in (1..|M_i|)
                P_i is the condition of the constraint which is a polynomial with |Mi| variables. 
                Q_i ∈ Fq[x] is the domain polynomial of the constraint which should vanish on the locations where the constraint should hold.
                (here we represent Q_i as a set of its' roots)
        """

        (field, d, C) = instantce
        self.field = field
        self.degree = d
        self.constraints = C        

        """Witness format: The witness w is a polynomial f ∈ Fq[x]. A constraint (M, P, Q) is said to hold at a location x ∈ Fq 
           if P(f(x * M_1), f(x * M_2), ..., f(x * M_|M|)) = 0
           We say that f satisfies the constraint if previous equality holds at every x ∈ Fq for which Q(x) = 0.
           We say that w satisfies the instance if and only if deg(f) < d and f satisfies all of the
           constraints. 
        """
        self.witness = witness

    def check_witness():
        assert(self.witness is not None, "Witness is undefined at this point.")

        if self.witness().degree > d:
            return False
        for M, P, Q in self.constraints:
            for x in Q:
                if P.evaluate([f.evaluate(x*m) for m in M]) != 0:
                    return False

        return True

    def set_witness(witness):
        self.witness = witness

    @classmethod
    def fromAIR(cls, AIR):
        assert(AIR.consistency_check(), "AIR instance is not fully defined.")
        field = AIR.field
        W = AIR.w
        T = AIR.T
        poly_ring = polynomialsOver(field, "X")

        mul_group_order = field.size() - 1
        if (mul_group_order % (W*T) != 0:
            raise StarkError("Unable to generate ARP instance for %s of size %d" %(field, W*T))

        gamma = field.get_prim_element() ** (mul_group_order / (W*T))
        full_mask = [gamma ** k for k in xrange(2*W)]
        Q = [gamma ** (W*k) for k in xrange(T)]
        С = [(full_mask, P, Q) for P in AIR.trace_constraints]
        C += [([1], X - alpha, [gamma**(i*W+j)]) for (i, j, alpha in AIR.boundary_constraints)]

        #TODO: how is degree defined?
        degree = T * w
        instance = (field, degree, C)

        if AIR.witness is not None:
            domain, values = zip(*[(gamma**(t*W+j), AIR.witness[j][t]) for  (t, j) in itertools.product(xrange(T), xrange(W))])
            witness = construct_interpolation_poly(poly_ring, domain, values)
        else:
            witness = None

        return cls(instance, witness)
        