from algebra.utils import *
from math import log

"""A class of linearized polynomials - i.e.,
univariate polynomials whose non-zero coefficients_ are only of monomials of the form  x^{p^i},
where p is the characterisctics of the undelying field
and possibly, a non-zero constant coefficient."""

@memoize
def LinearisedPolyRing(field):
    if not hasattr(field, "char") or not hasattr(field, "extension degree"):
        raise StarkError("Linearised polynomials are defined only over Finite Fields with p^n elements for n > 1.")

    class LinearisedPoly():
        def __init__(self, coeffs):
            self._coeffs = strip([self.field(x) for x in coeffs], self.field(0))
            self.reset()

        def reset(self):
            self._matrix = None
            self._is_zero = (len(self._coeffs) == 0)

        def evaluate(self, x):
           
		    """we take advantage of the fact that calculation Grobenius automorphism is very efficient in GFpE,
		        and that x^{p^i} = (x^{p^{i-1})^p. Each iteration we raise the current power
		        of x to p_th power, multiply it by the relevant coefficient, and add to the running sum"""

            running_sum = self.field(0);

            for coef in self._coeffs:
                running_sum += coef * x
                x = pow(x, self.p)
            return running_sum

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
            
        def multiplyByConstant(self, c):
            if c == self.field(0):
                self._coeffs = []
            else:   
                self._coeffs = [x * c for x in self._coeffs]
            self.reset()

        def _computeMatrix(self):
            dim = self.field.extension_degree


            x = self.field([0, 1])
            cur = self.field(1)

            for 
            void AffinePolynomial::computeMat() {
            const long dim = ExtensionDegree;

            if (coefficients_.size() == 0){
                polyMat_.fill(0);
                return;
            }
            

            for (long i = 0; i < dim; i++){
                const FieldElement x = mapIntegerToFieldElement(i, 1, 1);
                polyMat_[i] = mapFieldElementToInteger(0,ExtensionDegree,evalLinearPart(x,coefficients_));

            }
        }


        def getMatrix(self):
            if self._matrix is None:
                self._computeMatrix()
            return self._matrix
        
	

	
