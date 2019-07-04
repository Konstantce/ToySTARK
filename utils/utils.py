class StarkError(RuntimeError):
    def __init__(self, message):
        self.message = message
    def __str__(self):
      return repr(self.message)


#placeholder
class Placeholder():
   def init(self):
      pass
   def __repr__(self):
      return [ k for k,v in locals().iteritems() if v == self][0]

global p_
p_ = Placeholder()


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


# strip all copies of elt from the end of the list
def strip(L, elt):
   if len(L) == 0: return L

   i = len(L) - 1
   while i >= 0 and L[i] == elt:
      i -= 1

   return L[:i+1]
