from algebra.finite_field import *
from linearized_polynomials import *

from abc import ABCMeta, abstractmethod
import itertools 

"""
Here we define DomainIerarchy - crusial structure for the whole FRI-OPP protocol.
"""

class DomainIerarchy():
    __metaclass__ = ABCMeta

    def __init__(self):
        pass

    #NB: all of domain elements work with either a point p, or a tuple (p, trapdoor)
    #the concrete representation should be transparrent to end users
    #TODO: may be use a special Metaclass>

    #get the size of the i-th level:
    @abstractmethod     
    def get_domain_size(self, i):
        pass

    #check if point p belongs to the i-th level of DomainIerarchy
    @abstractmethod
    def is_in_domain(self, p, i):
        pass

    #assuming point p belongs to the i-th domain, get its image in the i+1 - domain,
    #which is equal to q_i(p)
    #NB: if p is a tuple (p, trapdoor) alsp returns a new value of trapdoor info 
    @abstractmethod
    def map_to_subdomain(self, p, i):
        pass

    #assuming point p belongs to the i-th level, return the corresponding coset of this point,
    #in other return p=p1, p2, .., pn all points in the i-th domain which map to the same value y under q_i 
     #NB: if p is a tuple (p, trapdoor) alsp returns a list of tuples 
    @abstractmethod
    def get_coset(self, p, i):
        pass

    #return coset iterator for the i-th domain
    @abstractmethod
    def get_coset_iter(self, i):
        pass

    #return element interator for the i-th domain
    @abstractmethod
    def get_domain_iter(self, i):
        pass
    
    #returns point (alongside with its' trapdoor information) from random bitstring
    #which should be the Python bytes types - a usual digest for different hash functions
    @abstractmethod
    def from_hash(self, data, i):
        pass
    
    #here where the trapdoor information is used - returns the position of point p
    # as it would be returned by the i-th level iterator 
    @abstractmethod
    def get_index(self, p, i):
        pass

    #assuming point y is in domain i >= 1, returns the list of its' preimages in domain i-1
    #this method is not necessary for implementing the FRI-OPP protocol, 
    # but os of certain use for debugging purposes 
    @abstractmethod 
    def get_preimage(self, y, i):
        pass

    #get the underlying finite field
    @abstractmethod
    def get_field(self):
        pass


class MultiplicativeDomainIerarchy(DomainIerarchy):
    def __init__(self, field, size, levels, nu = 1):
        group_order = field.get_num_of_elems() - 1
        if (group_order % size):
            raise StarkError("There is no multiplicative domain of size %d in %s." %(size, field))
        if size % (2 **(nu * (levels - 1))) != 0:
            raise StarkError("Specified size is to small to construct required number of levels.")

        mul_gen = field.get_prim_element()      
        omega = mul_gen ** (group_order / size)

        w_index = size / (2**nu)
        w = omega ** w_index
        self.w_index = w_index
        self.coset_gen = [w**k for k in xrange(2 ** nu)]

        self.field = field
        self.size = size
        self.levels = levels
        self.nu = nu
        self.omega = omega

    def get_domain_size(self, i):
        return self.size / (2**(self.nu * i))
   
    def is_in_domain(self, p, i):
        p = p[0] if isinstance(p, tuple) else p
        return p ** self.get_domain_size(i) == 1

    def map_to_subdomain(self, p, i):
        if isinstance(p, tuple):
            return (p[0] ** (2 ** self.nu), (p[1] * (2 ** self.nu)) % self.get_domain_size(i+1))
        else:
            return p ** (2 ** self.nu)

    def get_coset(self, p, i):
        if isinstance(p, tuple):
            return [(p[0] * w, (p[1] + i * self.w_index) %  self.get_domain_size(i)) for (i, w) in enumerate(self.coset_gen)]
        else:
            return [p * w for w in self.coset_gen]

    def _get_level_generator(self, i):
        return self.omega ** (2 ** (self.nu * i))

    def get_coset_iter(self, i):
        level_omega = self._get_level_generator(i)
        return (self.get_coset(level_omega ** j, i) for j in xrange(self.get_domain_size(i) / (2 ** self.nu)))

    def get_domain_iter(self, i):
        level_omega = self._get_level_generator(i)
        return (level_omega ** i for i in xrange(self.get_domain_size(i)))

    @staticmethod
    def _bitlen(x):
    	length = 0
        while (x):
            x >>= 1
            length += 1
        return length
    
    #returns point (alongside with its' trapdoor information) from random bitstring
    #which should be the Python bytes types - a usual digest for different hash functions
    def from_hash(self, data, i):
        if self._bitlen(self.get_domain_size(i)) >= len(data) * 8:
            raise StarkError("Provided bitstring is too short.")

        idx = sum(ord(c) << (i * 8) for i, c in enumerate(data)) % self.get_domain_size(i)
        return (self._get_level_generator(i) ** idx, idx)
           
    def get_index(self, p, i):
        if not isinstance(p, tuple):
            raise StarkError("No trapdoor information has been provided alongside the point.")
        return p[1]

    def get_preimage(self, y, i):
        y = y[0] if isinstance(y, tuple) else y

        if not self.is_in_domain(y, i):
            raise StarkError("Provided element %s is not in %d-th domain" %(y, i))
        
        #There is a deterministic algorithm to find n'th root of val in finite residue field,
        #google for "An Improvement of the Cipolla-Lehmer Type Algorithms" by Namhun Koo1, et al
        #however we just take succesive square roots
        preimage = [y]
        nu = self.nu
        while nu != 0:
            nu -= 1
            roots = []
            for v in preimage:
                x = v.sqrt()
                roots.extend([x, -x])
            preimage = roots
        return preimage
        
    def get_field(self):
        return self.field
 
        
class AdditiveDomainIerarchy(DomainIerarchy):
    """
    Given linear independent spanSet [e_1, ..., e_n] computes series of subspace polynomials vanishing exactly over the subspaces
    generated by (e1), (e1, e2), ... , (e1, e2, ..., e_m). If [e1, .., e_n are not linearly independent] returns None
    NB: our algoruthm only works for fields of characteristics 2

    For simplicity, let us first describe an alg that would work assuming {e1,..ek} are lin. independent:
	The algorithm would inductively computes the (coeffs of the) subspace polynomial P_i of the subspace spanned by {e_1,..,e_i}.
	For i=1, this is the polynomial x^2 + e1*x. Assume we have computed P_{i-1}.
	* it turns out that P_i is P_{i-1} composed from the outside with x^2 + P_{i-1}(e_i)*x
	* this is the formula the code implements.
	All this was assuming {e1,..,ek} were linearly independent.
	Now, to remove this assumption, before constructing the next P_i we check if the current e_i is linearly dependent
	on {e1,..,e_{i-1}} - we do this by simply checking if P_{i-1}(e_i) =0.
	If so, we simply let P_i= P_{i-1}.
	Otherwise, we derive P_i using the formula described above.
    (This algorithm is taken from libstark implementation)
    Note, that this way constructed subspace polynomial is linearized.
    """
    @classmethod
    def _construct_successive_subspace_polys(cls, spanSet):
        #some initial checks and definitions
        assert len(spanSet) != 0, "Spanning set of subspace is empty!" 
        field = spanSet[0].__class__
        assert hasattr(field, "char") and field.char == 2, "we work only in the fields of charactersitics 2."
        poly_ring = LinearisedPolyRing(field)
        res = []

        #initializing as the subspace poly of the space {0} - which is x
        poly = poly_ring([field(1)])
        for elem in spanSet:
            #compute c= P_{i-1}(e_i)
            c = poly.evaluate(elem)
            if c == field(0):
                return None
       
            poly = poly.frobenius_morphism() + poly.multiplyByConstant(c)
            res.append(poly)
        return res

    """
    Given spanset = [e1, e2, ..., e_n] we assume that the first domain is generated by
    [e1, e2, ..., e_(n - nu)], the second by [e_1, e_2, ..., e_(n - 2*nu)] and so on
    """
    def __init__(self, spanSet, levels, nu = 1):
        if len(spanSet) <= levels * nu:
            raise StarkError("Specified size is to small to construct required number of levels.")
        subspace_polys =  self._construct_successive_subspace_polys(spanSet)
        if subspace_polys is None:
            raise StarkError("Provided spanning set is not linear independent")
        
        self.basis = spanSet[::-1]
        self.subspace_polys = subspace_polys[::-nu][:levels]
        self.p = 2
        self.levels = levels
        self.nu = nu
       
    def get_domain_size(self, i):
        basis_len = len(self.basis) - i * self.nu
        return self.p**basis_len

    def is_in_domain(self, p, i):
        p = p[0] if isinstance(p, tuple) else p
        return self.subspace_polys[i].evaluate(p) == 0

    def _q_basis_generator(self, i):
        nu = self.nu
        y = (reduce((lambda c, (j,y): c + self.basis[nu * i + j] * y), enumerate(x), 0) for x in itertools.product(xrange(self.p), repeat = nu))

    def map_to_subdomain(self, val, i):
        #returns product of (val - x) for all x in subspace generated by [e_(nu *i), ..., e_(nu*(i+1) - 1)]
        #if isinstance(p, tuple):
        return reduce((lambda x, y: x * (val - y)), self._q_basis_generator(i), 1) 
 
    def get_coset(self, val, i):
        #if isinstance(p, tuple):
        return [val + x for x in self._q_basis_generator(i)]

    def get_coset_iter(self, i):
        coeffs = itertools.product(xrange(self.p), repeat = len(self.basis) - i - 1)
        disjoint_representatives = (reduce((lambda c, (j,y): c + self.basis[-j-1] * y), enumerate(x), 0) for x in coeffs)
        return (self.get_coset(x) for x in disjoint_representatives)

    def get_domain_iter(self, i):
        pass
    
    def from_hash(self, data, i):
        pass
    
    def get_index(self, p, i):       
        pass
    
    def get_preimage(self, y, i):
        pass
   
    def get_field(self):
        pass











