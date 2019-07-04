from random import randrange

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


def is_prime(p):
   def miller_rabin_test(n, k=10):
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

   return miller_rabin_test(p)


def jacobi(a, n):
   #calculate the Jacobi symbol (a, n) with n odd.
   #The result is either -1, 0 or 1
   assert(n % 2, ("%d is not odd: unable to compute Jacobi symbol" %n))

   t = 1
   a %= n
   while a != 0:
      while a % 2 == 0:
         a /= 2
         r = n % 8
         if r == 3 or r == 5:
            t = -t
      a, n = n, a
      if a % 4 == n % 4 == 3:
            t = -t
      a %= n
   return t if n == 1 else 0



       


