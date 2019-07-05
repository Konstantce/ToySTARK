from algebra.linear_algebra import *
from algebra.finite_field import *
from utils.utils import *

from math import log
import itertools

"""A class of linearized polynomials - i.e.,
univariate polynomials whose non-zero coefficients_ are only of monomials of the form  x^{p^i},
where p is the characterisctics of the undelying field
and possibly, a non-zero constant coefficient."""

@memoize
def LinearisedPolyRing(field):
    if not hasattr(field, "char"):
        raise StarkError("Linearised polynomials are defined only over finite fields.")

    class LinearisedPoly():
        def __init__(self, coeffs):
            self._coeffs = strip([self.field(x) for x in coeffs], self.field(0))
            self.reset()

        def reset(self):
            self._matrix = None
            self._is_zero = (len(self._coeffs) == 0)

        def evaluate(self, x):
            #we take advantage of the fact that calculation Frobenius automorphism is very efficient in GFpE,
		    #and that x^{p^i} = (x^{p^{i-1})^p. Each iteration we raise the current power of x to p_th power,
            #multiply it by the relevant coefficient, and add to the running sum.

            running_sum = self.field(0)
            for coef in self._coeffs:
                running_sum += coef * x
                x = pow(x, self.p)
            return running_sum

        def __add__(self, other):
            return LinearisedPoly([x + y for (x, y) in itertools.zip_longest(self._coeffs, other._coeffs, fillvalue=self.field(0))])

        @classmethod
        def _get_log(cls, n):
            v = int(log(n, self.p))
            return v if self.p **v == n else None
            
        #return the i'th coefficient of this polynomial
        def __getitem__(self, index):
            if self._is_zero:
                return self.field(0)
            else:
                v = self._get_log(index)
                return self._coeffs[v] if v is not None else self.field(0)

        def get_degree(self):
            return pow(self.p, len(self._coeffs)) if not self._is_zero else -1

        #raise poly to p-th power
        def frobenius_moprhism(self):
            return LinearisedPoly([self.field(0)] + [x**self.p for x in self._coeffs])
           
        def multiplyByConstant(self, c):
            if c == self.field(0):
                self._coeffs = []
            else:   
                self._coeffs = [x * c for x in self._coeffs]
            self.reset()

        def _computeMatrix(self):
            dim = self.field.extension_degree if hasattr(self.field, "extension_degree") else 1
            Mat = MatrixRing(IntegersModP(self.p))

            if self._is_zero:
                self._matrix = Mat.zero_matrix(dim)
            else:
                arr = []
                x = self.field([0, 1])
                cur = self.field(1)

                for i in xrange(dim):
                    y = self.evaluate(cur)
                    arr.append(y.poly.coefficients)
                    cur *= x
                    self._matrix = Mat(zer0)

        def getMatrix(self):
            if self._matrix is None:
                self._computeMatrix()
            return self._matrix
            
        
	LinearisedPoly.field = field
    LinearisedPoly.p = field.p
    return LinearisedPoly

	
