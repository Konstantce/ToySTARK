#this module comtains code for both univariate and multivariate polynomials
try:
    from itertools import zip_longest
except ImportError:
    from itertools import izip_longest as zip_longest

from itertools import ifilter
from utils.utils import *
from miscellaneous import *
import copy


# create a polynomial with coefficients in any integral domain; coefficients are in
# increasing order of monomial degree so that, for example, [1,2,3]
# corresponds to 1 + 2x + 3x^2
@memoize
def polynomialsOver(domain, variable_name = 'X'):

   class Polynomial(DomainElement):
      operatorPrecedence = 2 if not hasattr(domain, 'is_poly') else 1 + domain.operatorPrecedence

      @classmethod
      def factory(cls, L):
         return Polynomial([cls.domain(x) for x in L])

      @classmethod
      def _init_from_subdomain(cls, val, verbose = False):
         if verbose:
            print val
         
         if isinstance(val, cls.domain):
            return val
         
         cur_domain = cls.domain
         domain_stack = []

         while True:
            domain_stack.append(cur_domain)
            if verbose:
               print cur_domain
            if cur_domain == cls.base_field:
               break
            cur_domain = cur_domain.domain
            if isinstance(val, cur_domain):
               break
            
         
         for dom in reversed(domain_stack):
            val = dom(val)
         return val

      def __init__(self, c):
         #TODO: fix when initing from polynomials on subdomains
         if type(c) is Polynomial:
            self.coefficients = copy.deepcopy(c.coefficients)
         elif not isinstance(c, (list, tuple)):
            self.coefficients = [self._init_from_subdomain(c)]
         else:
            self.coefficients = [self._init_from_subdomain(x) for x in c]

         self.coefficients = strip(self.coefficients, self.domain(0))

      def isZero(self): return self.coefficients == []

      def __abs__(self): return len(self.coefficients) # the valuation only gives 0 to the zero polynomial, i.e. 1+degree
      def __len__(self): return len(self.coefficients)
      def __sub__(self, other): return self + (-other)
      def __iter__(self): return iter(self.coefficients)
      def __neg__(self): return Polynomial([-a for a in self])

      def iter(self): return self.__iter__()
      def leadingCoefficient(self): return self.coefficients[-1]
      def degree(self): return abs(self) - 1

      @typecheck
      def __eq__(self, other):
         return self.degree() == other.degree() and all([x==y for (x,y) in zip(self, other)])

      @typecheck
      def __ne__(self, other):
          return self.degree() != other.degree() or any([x!=y for (x,y) in zip(self, other)])

      @typecheck
      def __add__(self, other):
         newCoefficients = [sum(x) for x in zip_longest(self, other, fillvalue=self.domain(0))]
         return Polynomial(newCoefficients)

      @typecheck
      def __mul__(self, other):
         if self.isZero() or other.isZero():
            return Zero()

         newCoeffs = [self.domain(0) for _ in range(len(self) + len(other) - 1)]

         for i,a in enumerate(self):
            for j,b in enumerate(other):
               newCoeffs[i+j] += a*b

         return Polynomial(newCoeffs)

      @typecheck
      def __divmod__(self, divisor):
         #divmod is defined only for unavariate polynomails
         assert self.domain == self.base_field, "Divmod is not properly defined for multivariate polynomials"

         quotient, remainder = Zero(), self
         divisorDeg = divisor.degree()
         divisorLC = divisor.leadingCoefficient()

         while remainder.degree() >= divisorDeg:
            monomialExponent = remainder.degree() - divisorDeg
            monomialZeros = [self.domain(0) for _ in range(monomialExponent)]
            monomialDivisor = Polynomial(monomialZeros + [remainder.leadingCoefficient() / divisorLC])

            quotient += monomialDivisor
            remainder -= monomialDivisor * divisor

         return quotient, remainder

      @typecheck
      def __truediv__(self, divisor):
         if divisor.isZero():
            raise ZeroDivisionError
         return divmod(self, divisor)[0]


      @typecheck
      def __mod__(self, divisor):
         if divisor.isZero():
            raise ZeroDivisionError
         return divmod(self, divisor)[1]
    
      def __repr__(self):
         if self.isZero():
            return '0'

         return ' + '.join(['%s*%s^%d' % (a, variable_name, i) if i > 0 else '%s'%a 
                              for i,a in filter(lambda (i, x): x != self.domain(0), enumerate(self.coefficients))])
      
             
      #partial evaluation of multivariate polynomials
      def evaluate(self, points):
         if not hasattr(points, '__iter__'):
                points = [points]
         
         if self.domain == self.base_field:
            if len(points) != 1:
                  raise StarkError("Coeffs len for evaluation is of inproper length")
            val = points[0]
         else:
            self.coefficients = [self.domain.evaluate(x, points[:-1]) for x in self]
            val = points[-1]

         if isinstance(val, Placeholder):
            return self
         else:
            x = self.base_field(val)
            func = lambda (i, coeff): coeff * (x**i)
            return sum(map(func, enumerate(self)) , self.base_field(0))

      def __call__(self, coeffs):
         return self.evaluate(coeffs)

      @classmethod
      def from_string(cls, data):
         try:
            return eval(data)
         except:
            raise StarkError("Unable to construct polynomial from string: " + data)

   def Zero():
      return Polynomial([0])

   Polynomial.domain = domain
   Polynomial.variable_name = variable_name
   Polynomial.__name__ = '(%s)[%s]' % (domain.__name__, variable_name)
   Polynomial.is_poly = True
   Polynomial.base_field = domain.base_field if hasattr(domain, 'is_poly') else domain

   globals()[variable_name] = Polynomial([0, 1])
   return Polynomial


@memoize
def multiivar_polynomialsOver(domain, *variable_name_list):
   cur_domain = domain
   for var_name in variable_name_list:
      cur_domain = polynomialsOver(cur_domain, var_name)
   return cur_domain


def construct_interpolation_poly(poly_ring, domain, values):
   assert len(domain) == len(values), "The lengths of domain and values vectors are different!"
   assert isinstance(values[0], poly_ring.domain), "Inconsistency of types."
  
   poly = poly_ring(0)
   t = poly_ring([0, 1])
   for i in xrange(len(domain)):
      pred = (lambda k : k != i)
      func = (lambda x, j: x * (t - domain[j])/(domain[i] - domain[j]))
      prod = reduce(func, ifilter(pred, xrange(len(domain))), poly_ring(1))
      poly += values[i] * prod	

   return poly


class PolyProxy():
   def __init__(self, poly_ring, data):
      self.as_func, self.as_table = (None, data) if isinstance(data, dict) else (data, {})
      self.poly_ring = poly_ring

   def _interpolate_from_table(self):
      domain, values = zip(*self.as_table.items())
      self.as_func = construct_interpolation_poly(self.poly_ring, domain, values) 
         
   def __call__(self, x):
      if x in self.as_table:
         return self.as_table[x]
      else:
         if self.as_func is None:
            self._interpolate_from_table()         
         return self.as_func.evaluate(x)
            
   def get_coefficients(self):
      if self.as_func is None:
         self._interpolate_from_table()  
      return self.as_func.coefficients  

