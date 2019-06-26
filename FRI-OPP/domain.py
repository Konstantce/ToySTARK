from algebra.finite_field import *


class Domain():
    def __init__():
        pass

    @abstractmethod
    def get_subdomain():
        pass

    @abstractmethod
    def is_in_domain(val):
        pass

    @abstarctmethod
    def get_domain_size():
        pass

    @abstractmethod
    def map_to_subdomain(val):
        pass

    @abstractmethod
    def construct_coset_interpolation_poly(val, poly):
        pass


class MultiplicativeDomain(Domain):
    def __init__(field, size):
        self.size = size
        mul_gen = field.get_mult_gen()


class AdditiveDomain(Domain):






@memoize
def get_domain(domain, variable_name):
    def 










