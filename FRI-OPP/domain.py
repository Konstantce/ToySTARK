from algebra.finite_field import *
from linearized_polynomials import * 

#TODO: may be rewrite it using metaclasses?
#for now I use decorators
class Domain():
    def __init__(self):
        pass

    @abstractmethod     
    def get_domain_size(self):
        pass

    @abstractmethod
    def get_subdomain(self):
        pass

    @abstractmethod
    def is_in_domain(self, val):
        pass

    @abstractmethod
    def map_to_subdomain(self, val):
        pass

    @abstractmethod
    def get_coset(self, val):
        pass

    @abstractmethod
    def is_subdomain_defined(self):
        pass

    class check_subdomain_decorator(object):
        def __init__(decorated):
            self._decorated = decorated
        def __call__(instance, *args, **kwargs):
            if not instance.is_subdomain_defined():
                raise StarkError("The subdomain is undefined - unable to call %s method" % decorated.__name__)
            return decorated(instance, *args, **kwargs)


class MultiplicativeDomain(Domain):
    __init__flag = False

    def set_params(self, field, size, nu, omega, has_subdomain):
        self.field = field
        self.size = size
        self.nu = nu
        self.omega = omega
        self.has_subdomain = has_subdomain

    @classmethod
    def construct_domain(cls, field, size, nu = 2):
        if field.is_extension_field:
            raise StarkError("Multiplicative domain can be constructed only for residue fields.")
        group_order = field.get_num_of_elems() - 1
        if (group_order % size):
            raise StarkError("There is no multiplicative domain of size %d in %s.", %(size, field))

        mul_gen = field.get_prim_element()      
        omega = mul_gen ** (group_order / size)

        self.__init_flag = True
        domain = cls(self.omega, size, nu)
        self.__init_flag = False
        return domain
   
    def __init__(self, omega, size, nu = 2):
        if not self.__init_flag:
            raise StarkError("This constructor should be called only from get subdomain method.")
        self.set_params(omega.__class__, size, nu, omega, size <= nu)

    def is_in_domain(self, val):
        return val ** self.size == 1

    @check_subdomain_decorator
    def get_subdomain(self):
        self.__init_flag = True
        subdomain = self.__class__(self.omega ** nu, self.size /= nu, nu)
        self.__init_flag = False
        return subdomain

    @check_subdomain_decorator
    def map_to_subdomain(self, val):
        return val ** self.nu

    @check_subdomain_decorator
    def get_coset(self, val):      
        if (not self.get_subdomain().is_in_domain(val)):
            raise StarkError("Provided element %s is not in subdomain" %val)

        #There is a deterministic algorithm to find n'th root of val in finite residue field,
        #google for "An Improvement of the Cipolla-Lehmer Type Algorithms" by Namhun Koo1, Gook Hwa Cho2, Byeonghwan Go2, and Soonhak Kwon
        #however we just take succesive square roots (we have silently assumed that nu is a power of 2 here)
        coset = [val]
        nu = self.nu

        while nu != 1:
            assert(nu %2 == 0, "In current implementation we assumed that nu is power of 2")
            nu /= 2
            roots = []
            for v in coset:
                x = v.sqrt()
                roots.append(x)
                roots.append(-x)
            coset = roots

        return coset

    def get_domain_size(self):
        return self.size

    def is_subdomain_defined(self):
        return self.has_subdomain


class AdditiveDomain(Domain):
    """  
    Computes the subspace polynomial that vanishes exactly over the span of spanSet (NB: only works for fields of characteristics 2)
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
    Note, that thus constructed subspace polynomial is linearized
    """
    @classmethod
    def _construct_subspace_poly(cls, spanSet):
        #some initial checks and definitions
        assert(len(spanSet) != 0, "Spanning set of subspace is empty!")
        field = spanSet[0].__class__
        assert(hasattr(field, "char") and field.char == 2, "Subspace polynomial creation algorithm is valid only for fields of char 2")
        poly_ring = LinearisedPolyRing(field)

        #apart from subspace polynomial we return the basis of this subspacem that is
        #the linear independent subset of spanning set
        basis = []

        #initializing as the subspace poly of the space {0} - which is x
        poly = poly_ring([field(1)])
        for elem in in spanSet:
            #compute c= P_{i-1}(e_i)
            c = poly.evaluate(elem)
            if c == field(0):
                continue

            basis.append(elem)          
            poly = poly.frobenius_morphism() + poly.multiplyByConstant(c)
        return poly

    def __init__(self, spanSet, dim, roots = None, gen_random_roots = True):
        self.subspace_poly, self.basis = cls._construct_subspace_poly(spanSet)
        self.q = None
        self.q_matrix = None

        if roots is not None:
            if any([self.subspace_poly(x) != field(0) for x in roots]):
                raise StarkError("Roots do not belong to constructed subspace.")
            self.q = self._construct_q_poly(roots)


            #check if all of them are in subdomain and them construct subspace polynomial
            #there is also a special matrix assiciated with subspace polynomial - what is it used for?
            subdomain_defined = True

    @abstractmethod     
    def get_domain_size(self):
        pass

    @abstractmethod
    def get_subdomain(self):
        pass

    @abstractmethod
    def is_in_domain(self, val):
        pass

    @abstractmethod
    def map_to_subdomain(self, val):
        pass

    @abstractmethod
    def get_coset(self, val):
        pass

    @abstractmethod
    def is_subdomain_defined(self):
        pass





@memoize
def get_domain(domain, variable_name):
    def 










