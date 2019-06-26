from algebra.finite_field import *


class Domain():
    def __init__(self, field, size, nu = 2):
        self.field = field
        self.size = size
        self.nu = nu
              
    def get_domain_size(self):
        return size

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
    def construct_coset_interpolation_poly(self, val, poly):
        pass


class MultiplicativeDomain(Domain):
    def __init__(self, field, size, nu = 2):
        Domain.__init__(field, size, nu)
        mul_gen = field.get_prim_element()
        group_order = field.get_num_of_elems() - 1
        if (group_order % size):
            raise StarkError("There is no multiplicative domain of size %d in %s.", %(size, field))
        self.omega = mul_gen ** (group_order / size)
       
    def __init__(self, omega, size, nu = 2):
        Domain.__init__(omega.__class__, size, nu)
        self.omega = omega

    def get_subdomain(self):
        if size <= nu:
            raise StarkError("Impossible to construct subdomain: the domain itself is too small")
        return self.__class__(self.omega ** nu, self.size /= nu, nu)

    def is_in_domain(val):
        return val ** self.size == 1

    def map_to_subdomain(val):
        return val ** self.nu

    def construct_coset_interpolation_poly(val, poly):
        
@classmethod
    def instance(cls):
        if not hasattr(cls, '_instance'):
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        assert not hasattr(self.__class__, '_instance'), 'Do not call constructor directly!'



class AdditiveDomain(Domain):






@memoize
def get_domain(domain, variable_name):
    def 










