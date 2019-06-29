from algebra.finite_field import *

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

    def __init__(self, field, size, nu = 2):
        if field.is_extension_field:
            raise StarkError("Multiplicative domain can be constructed only for residue fields.")
        group_order = field.get_num_of_elems() - 1
        if (group_order % size):
            raise StarkError("There is no multiplicative domain of size %d in %s.", %(size, field))

        mul_gen = field.get_prim_element()      
        self.omega = mul_gen ** (group_order / size)
        self.set_params(field, size, nu, omega, size <= nu)
       
    def __init__(self, omega, size, nu = 2):
        if not self.__init_flag:
            raise StarkError("This constructor should be called only from get subdomain method.")
        self.set_params(omega.__class__, size, nu, omega, size <= nu)

    def is_in_domain(self, val):
        return val ** self.size == 1

    @check_subdomain_decorator
    def get_subdomain(self):
        self.__init_flag = True
        res= self.__class__(self.omega ** nu, self.size /= nu, nu)
        self.__init_flag = False
        return res

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
    """
    def construct_subspace_poly(self, spanSet, check_if_basis = False):
        base_field = spanSet
        if (spanSet.size() == 0){
            vector<FieldElement> idPoly(1);
            idPoly[0] = one();
            return idPoly;
        }


		//Initializing as the subspace poly of the space {0} - which is x
		coefficients.push_back(one());
		FieldElement c, eiPower;
		unsigned int i = 0, j;
		elementsSet_t::iterator z = spanSet.begin();
		while (z != spanSet.end()){
			//compute c= P_{i-1}(e_i)
			c = zero();

			eiPower = *z; 	//eiPower starts as ei
			for (j = 0; j < coefficients.size(); j++) {
				c += coefficients[j] * eiPower;
				eiPower = sqr(eiPower);
			}
			//Now check if c is non-zero - which means e_i is independent of previous ej's.
			if (!(c == zero())){
				//if so, update P_i to be zero on the extended span of {e1,..ei}
				i++;
				coefficients.push_back(one());
				for (j = i - 1; j >= 1; j--) {
					coefficients[j] = c*coefficients[j] + sqr(coefficients[j - 1]);
				}
				coefficients[0] = c*coefficients[0];

			}
			z++;
		}
			return coefficients;

    def __init__(basis, linearized_poly_roots = None):
        self.base_field = basis[0].field
        self.poly_ring = polynomialsOver(self.base_field)
        self.subspace_poly = construct_subspace_poly(basis, True)
        if self.subspace_poly is None:
            raise StarkError("Generating set is not linearly independent")
        
        if linearized_poly_roots in not None:
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










