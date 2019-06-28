from random import randrange

# a general Euclidean algorithm for any number type with
# a divmod and a valuation abs() whose minimum value is zero
def gcd(a, b):
   if abs(a) < abs(b):
      return gcd(b, a)

   while abs(b) > 0:
      _,r = divmod(a,b)
      a,b = b,r

   return a


# extendedEuclideanAlgorithm: int, int -> int, int, int
# input (a,b) and output three numbers x,y,d such that ax + by = d = gcd(a,b).
# Works for any number type with a divmod and a valuation abs()
# whose minimum value is zero
def extendedEuclideanAlgorithm(a, b):
   if abs(b) > abs(a):
      (x,y,d) = extendedEuclideanAlgorithm(b, a)
      return (y,x,d)

   if abs(b) == 0:
      return (1, 0, a)

   x1, x2, y1, y2 = 0, 1, 1, 0
   while abs(b) > 0:
      q, r = divmod(a,b)
      x = x2 - q*x1
      y = y2 - q*y1
      a, b, x2, x1, y2, y1 = b, r, x1, x, y1, y

   return (x2, y2, a)


# memoize calls to the class constructors for fields
# this helps typechecking by never creating two separate
# instances of a number class.
def memoize(f):
   cache = {}

   def memoizedFunction(*args, **kwargs):
      argTuple = args + tuple(kwargs)
      if argTuple not in cache:
         cache[argTuple] = f(*args, **kwargs)
      return cache[argTuple]

   memoizedFunction.cache = cache
   return memoizedFunction


# type check a binary operation, and silently typecast 0 or 1
def typecheck(f):
   def newF(self, other):
      if (hasattr(other.__class__, 'operatorPrecedence') and
            other.__class__.operatorPrecedence > self.__class__.operatorPrecedence):
         return NotImplemented

      if type(self) is not type(other):
         try:
            other = self.__class__(other)
         except TypeError:
            message = 'Not able to typecast %s of type %s to type %s in function %s'
            raise TypeError(message % (other, type(other).__name__, type(self).__name__, f.__name__))
         except Exception as e:
            message = 'Type error on arguments %r, %r for functon %s. Reason:%s'
            raise TypeError(message % (self, other, f.__name__, type(other).__name__, type(self).__name__, e))

      return f(self, other)

   return newF



# require a subclass to implement +-* neg and to perform typechecks on all of
# the binary operations finally, the __init__ must operate when given a single
# argument, provided that argument is the int zero or one
class DomainElement(object):
   operatorPrecedence = 1

   # the 'r'-operators are only used when typecasting ints
   def __radd__(self, other): return self + other
   def __rsub__(self, other): return -self + other
   def __rmul__(self, other): return self * other

   # square-and-multiply algorithm for fast exponentiation
   def __pow__(self, n):
      if type(n) is not int:
         raise TypeError

      Q = self
      R = self if n & 1 else self.__class__(1)

      i = 2
      while i <= n:
         Q = (Q * Q)

         if n & i == i:
            R = (Q * R)

         i = i << 1

      return R


   # requires the additional % operator (i.e. a Euclidean Domain)
   def powmod(self, n, modulus):
      if type(n) is not int:
         raise TypeError

      Q = self
      R = self if n & 1 else self.__class__(1)

      i = 2
      while i <= n:
         Q = (Q * Q) % modulus

         if n & i == i:
            R = (Q * R) % modulus

         i = i << 1

      return R


class StarkError(RuntimeError):
   def __init__(self, message):
      self.message = message
   def __str__(self):
      return repr(self.message)


def miller_rabin(n, k=10):
   if n == 2 or n == 3:
		return True
   if not n & 1:
      return False

   def check(a, s, d, n):
      x = pow(a, d, n)
      if x == 1:
         return True
      for i in xrange(s - 1):
         if x == n - 1:
            return True
         x = pow(x, 2, n)
      return x == n - 1

   s = 0
   d = n - 1

   while d % 2 == 0:
      d >>= 1
      s += 1

   for i in xrange(k):
      a = randrange(2, n - 1)
      if not check(a, s, d, n):
         return False
   return True


def is_prime(p):
   return miller_rabin(p)


def legendre_symbol(a, p):
   #calculate the legendre symbol (a, p) with p is prime.
   #The result is either -1, 0 or 1
   assert(is_prime(p), "%d is not prime: unable to compute Legendre symbol", %p)

   if a >= p or a < 0:
        return calculateLegendre(a % p, p)
    elif a == 0 or a == 1:
        return a
    elif a == 2:
        if p%8 == 1 or p%8 == 7:
            return 1
        else:
            return -1
    elif a == p-1:
        if p%4 == 1:
            return 1
        else:
            return -1
    elif not isPrime(a):
        factors = factorize(a)
        product = 1
        for pi in factors:
            product *= calculateLegendre(pi, p)
        return product
    else:
        if ((p-1)/2)%2==0 or ((a-1)/2)%2==0:
            return calculateLegendre(p, a)
        else:
            return (-1)*calculateLegendre(p, a)

#placeholder
class Placeholder():
   def init(self):
      pass
   def __repr__(self):
      return [ k for k,v in locals().iteritems() if v == self][0]


global p_
p_ = Placeholder()
       


