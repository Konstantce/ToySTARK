from polynomials import *
import random


# additionally require inverse() on subclasses
class FieldElement(DomainElement):
   def __truediv__(self, other): return self * other.inverse()
   def __rtruediv__(self, other): return self.inverse() * other
   def __div__(self, other): return self.__truediv__(other)
   def __rdiv__(self, other): return self.__rtruediv__(other)


# so all IntegersModP are instances of the same base class
class _Modular(FieldElement):
   pass


@memoize
def IntegersModP(p, prim_element = None):
   # check if p is prime
   if not is_prime(p):
      raise StarkError("%s is not prime, so can't be used to generate finite field." % (p))

   class IntegerModP(_Modular):
      def __init__(self, n):
         try:
            self.n = int(n) % IntegerModP.p
         except:
            raise TypeError("Can't cast type %s to %s in __init__" % (type(n).__name__, type(self).__name__))

         self.field = IntegerModP

      @typecheck
      def __add__(self, other):
         return IntegerModP(self.n + other.n)

      @typecheck
      def __sub__(self, other):
         return IntegerModP(self.n - other.n)

      @typecheck
      def __mul__(self, other):
         return IntegerModP(self.n * other.n)

      def __neg__(self):
         return IntegerModP(-self.n)

      @typecheck
      def __eq__(self, other):
         return isinstance(other, IntegerModP) and self.n == other.n

      @typecheck
      def __ne__(self, other):
         return isinstance(other, IntegerModP) is False or self.n != other.n

      @typecheck
      def __divmod__(self, divisor):
         q,r = divmod(self.n, divisor.n)
         return (IntegerModP(q), IntegerModP(r))

      def inverse(self):
         # need to use the division algorithm *as integers* because we're
         # doing it on the modulus itself (which would otherwise be zero)
         x,y,d = extendedEuclideanAlgorithm(self.n, self.p)

         if d != 1:
            raise Exception("Error: p is not prime in %s!" % (self.__name__))

         return IntegerModP(x)

      def __abs__(self):
         return abs(self.n)

      def __str__(self):
         return str(self.n)

      def __repr__(self):
         return '%d (mod %d)' % (self.n, self.p)

      def __int__(self):
         return self.n

      @classmethod
      def get_prim_element(cls):
         if cls.prim_element is None:
            cls.set_prim_element()
         return cls.prim_element
            
      @classmethod
      def _check_if_prim_elem(cls, val):
         if cls.p == 2:
            return val == 1
         else:
            test_degree = (self.p - 1) / 2
            return cls(val)**test_degree == -1

      @classmethod
      def set_prim_element(cls, gen = None):
         if gen is not None:
            if cls._check_if_prim_elem(gen):
               cls.prim_element = cls(gen)
            else:
               raise StarkError("Provided element %d is not a primitive root for Z/%d." % (gen, p))
            else:
               #no generator is supplied, we'll construct it ourself by trial and error method
               v = cls(random.randrange(cls.p)
               while not cls._check_if_prim_elem(v):
                  v = cls(random.randrange(cls.p)
               cls.prim_element = cls(v)

      @classmethod
      def get_num_of_elems(cls):
         return cls.p

      @classmethod
      def get square_nonresidue(cls):
         if IntegerModp.p = False

      def sqrt(self):
         if self.p == 2:
            return IntegerModP(self.n)
         else if self.p % 4 == 3:
            k = (self.p - 3) / 4
            a = pow(self.n, k + 1, self.p)
            return IntegersModP(a)
         else if self.p % 4 == 1:
               
         else:
            raise StarkError("Unexpected error in sqrt method for finite field.")
           

   IntegerModP.p = p
   IntegerModP.is_extension_field = False
   
   #Predefined-nonresidue is used in sqrt method
   IntegerModp.square_nonresidue = None

   if prim_element:
      if not IntegerModP._check_if_prim_elem(prim_element):
         raise StarkError("Provided element %d is not a primitive root for Z/%d." % (prim_element, p))
      else:
         IntegerModP.prim_elem = IntegerModP(prim_element)
   else:
      IntegerModP.prim_elem = None
   IntegerModP.__name__ = 'Z/%d' % (p)
   IntegerModP.englishName = 'IntegersMod%d' % (p)
   return IntegerModP


# isIrreducible: Polynomial, int -> bool
# determine if the given monic polynomial with coefficients in Z/p is
# irreducible over Z/p where p is the given integer
# Algorithm 4.69 in the Handbook of Applied Cryptography
def isIrreducible(polynomial, p):
   ZmodP = IntegersModP(p)
   if polynomial.domain is not ZmodP:
      raise TypeError("Given a polynomial that's not over %s, but instead %r" %
                        (ZmodP.__name__, polynomial.field.__name__))

   poly = polynomialsOver(ZmodP, polynomial.variable_name).factory
   x = poly([0,1])
   powerTerm = x
   isUnit = lambda p: p.degree() == 0

   for _ in range(int(polynomial.degree() / 2)):
      powerTerm = powerTerm.powmod(p, polynomial)
      gcdOverZmodp = gcd(polynomial, powerTerm - x)
      if not isUnit(gcdOverZmodp):
         return False

   return True


# generateIrreduciblePolynomial: int, int -> Polynomial
# generate a random irreducible polynomial of a given degree over Z/p, where p
# is given by the integer 'modulus'. This algorithm is expected to terminate
# after 'degree' many irreducilibity tests. By Chernoff bounds the probability
# it deviates from this by very much is exponentially small.
def generateIrreduciblePolynomial(modulus, degree, variable):
   Zp = IntegersModP(modulus)
   Polynomial = polynomialsOver(Zp, variable)

   while True:
      coefficients = [Zp(random.randint(0, modulus-1)) for _ in range(degree)]
      randomMonicPolynomial = Polynomial(coefficients + [Zp(1)])

      if isIrreducible(randomMonicPolynomial, modulus):
         return randomMonicPolynomial


# create a type constructor for the finite field of order p^m for p prime, m >= 1
@memoize
def FiniteField(p, m, polynomialModulus=None, variable='t'):
   Zp = IntegersModP(p)
   if m == 1:
      return Zp

   Polynomial = polynomialsOver(Zp, variable)
   if polynomialModulus is None:
      polynomialModulus = generateIrreduciblePolynomial(modulus=p, degree=m, variable=variable)
   else:
      if not isIrreducible(polynomialModulus, p):
         raise StarkError("Provided polynomial %s is not irreducible" % polynomialModulus)

   class Fq(FieldElement):
      fieldSize = int(p ** m)
      primeSubfield = Zp
      idealGenerator = polynomialModulus
      operatorPrecedence = 3

      def __init__(self, poly):
         if type(poly) is Fq:
            self.poly = poly.poly
         elif type(poly) is int or type(poly) is Zp:
            self.poly = Polynomial([Zp(poly)])
         elif isinstance(poly, Polynomial):
            self.poly = poly % polynomialModulus
         else:
            self.poly = Polynomial([Zp(x) for x in poly]) % polynomialModulus

         self.field = Fq

      @typecheck
      def __add__(self, other): return Fq(self.poly + other.poly)
      @typecheck
      def __sub__(self, other): return Fq(self.poly - other.poly)
      @typecheck
      def __mul__(self, other): return Fq(self.poly * other.poly)
      @typecheck
      def __eq__(self, other): return isinstance(other, Fq) and self.poly == other.poly
      @typecheck
      def __ne__(self, other): return not self == other
      
      #def __pow__(self, n): return Fq(pow(self.poly, n))
      def __pow__(self, n):
         if n==0: return Fq([1])
         if n==1: return self
         if n%2==0:
            sqrut = self**(n//2)
            return sqrut*sqrut
         if n%2==1: return (self**(n-1))*self

      def __neg__(self): return Fq(-self.poly)
      def __abs__(self): return abs(self.poly)
      def __repr__(self): return repr(self.poly) + ' in ' + self.__class__.__name__

      @typecheck
      def __divmod__(self, divisor):
         q,r = divmod(self.poly, divisor.poly)
         return (Fq(q), Fq(r))


      def inverse(self):
         if self == Fq(0):
            raise ZeroDivisionError

         x,y,d = extendedEuclideanAlgorithm(self.poly, self.idealGenerator)
         if d.degree() != 0:
            raise Exception('Somehow, this element has no inverse! Maybe intialized with a non-prime?')

         return Fq(x) * Fq(d.coefficients[0].inverse())

      @classmethod
      def get_prim_element(cls):
         if cls.prim_element is None:
            raise StarkError("Primitive element should be manually set before retrieving.")
         return cls.prim_element
            
      @classmethod
      def set_prim_element(cls, gen):
         cls.prim_element = cls(gen)

      def get_num_of_elems(cls):
         return cls.fieldSize

   Fq.__name__ = 'F_{%d^%d}' % (p,m)
   Fq.prim_elem = None
   Fq.is_extension_field = True
   return Fq