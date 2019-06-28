from algebra.finite_field import *


class Domain():
    def __init__(self):
        pass

    @abstractmethod     
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
    def get_coset(self, val):
        pass


class MultiplicativeDomain(Domain):
    __init__flag = False

    def set_params()

    def __init__(self, field, size, nu = 2):
        if field.is_extension_field:
            raise StarkError("Multiplicative domain can be constructed only for residue fields.")
        group_order = field.get_num_of_elems() - 1
        if (group_order % size):
            raise StarkError("There is no multiplicative domain of size %d in %s.", %(size, field))
        
        Domain.__init__(field, size, nu)
        mul_gen = field.get_prim_element()      
        self.omega = mul_gen ** (group_order / size)

        self.field = field
        self.size = size
        self.nu = nu
       
    def __init__(self, omega, size, nu = 2):
        if not self.__init_flag:
            raise StarkError("This constructor should be called only from get subdomain method.")

        self.omega = omega
        self.field = omega.__class__
        self.size = size
        self.nu = nu

    def get_subdomain(self):
        if size <= nu:
            raise StarkError("Impossible to construct subdomain: the domain itself is too small")
        self.__init_flag = True
        res= self.__class__(self.omega ** nu, self.size /= nu, nu)
        self.__init_flag = False
        return res

    def is_in_domain(self, val):
        return val ** self.size == 1

    def map_to_subdomain(self, val):
        return val ** self.nu

    def get_coset(self, val):
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


class AdditiveDomain(Domain):
    def __init__()





@memoize
def get_domain(domain, variable_name):
    def 










