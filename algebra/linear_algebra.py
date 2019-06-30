from utils import DomainElement
from fractions import Fraction
import itertools
import copy

@memoize
def MatrixRing(domain = Fraction):

    class Matrix(DomainElement):
        def __init__(self, array):
            if not array:
                return
            assert(all(len(row) == len(arr[0]) for row in array), "the rows of matrix are of different length.")
            self.x_dim = len(array)
            self.y_dim = len(arr[0])
            self.data = array

        @classmethod
        def zero_matrix(cls, x_dim, y_dim = x_dim):
            mat = cls(None)           
            mat.x_dim = x_dim
            mat.y_dim = y_dim
            mat.data = [[self.domain(0)] * y_dim] * x_dim]
            return mat

        def __getitem__(self, index):
            return self.data[index]

        def __add__(self, other):
            assert(self.x_dim == other.x_dim and self.y_dim == other.y_dim, "The matrix dimensions of operands do not coincide")
            res = Matrix(copy.deepcopy(self.data))
            for i, j in itertools.product(xrange(self.x_dim), xrange(self.y_dim)):
                res[i][j] += othe[i][j]
            return self

        def __sub__(self, other):
            assert(self.x_dim == other.x_dim and self.y_dim == other.y_dim, "The matrix dimensions of operands do not coincide")
            res = Matrix(copy.deepcopy(self.data))
            for i, j in itertools.product(xrange(self.x_dim), xrange(self.y_dim)):
                res[i][j] += other[i][j]
            return self

        def __mul__(self, other):
            assert(self.y_dim == other.x_dim, "error in matrix multiplication: incorrect dimensions")
            arr = []
            for i in xrange(self.x_dim):
                row = []
                for j in xrange(other.y_dim):
                    running_sum = self.domain(0)
                    for k in xrange(self.y_dim):
                        running_sum += self.data[i][k] * other.data[k][j]
                    row.append(running_sum)
                arr.append(row)
            return Matrix(arr)

        def __neg__(self):
            arr = [[None] * self.y_dim] * self.x_dim
            for i, j in itertools.product(xrange(self.x_dim), xrange(self.y_dim)):
                arr[i][j] = -self.arr[i][j]
            return Matrix(arr)
   
        def __eq__(self, other):
            if self.x_dim != other.x_dim or self.y_dim != other.y_dim:
                return False
            return all([self.data[i][j] == other.data[i][j] for i, j in itertools.product(xrange(self.x_dim), xrange(self.y_dim))])
            
        def __ne__(self, other):
            return not self.__eq__(other)

        def __str__(self):
            return '\n'.join([''.join(['{:4}'.format(item) for item in row]) for row in self.data]))

        def det(self):
            assert(self.x_dim == self.y_dim, "Determinant is defined only for square matrices.")

            #if dimension of matrix is not very large compute it by definition
            if self.x_dim <= 6:
                running_sum = self.domain(0)
                for perm in itertools.permutations(range(self.x_dim)):
                    sign = 1 if len(filter(lambda (x, y): x < y, itertools.combinations(perm, 2))) % 2 == 0 else -1
                    running_sum += sign * sum([self.data[i][j] for (i, j) in enumerate(perm)])
                return running_sum
            else:
                P, L, U = self.get_PLU_decomposition()
                sign = 1 if len(filter(lambda (x, y): x < y, itertools.combinations(P, 2))) % 2 == 0 else -1

            #in the case det > 6 - find the determinant from the PLU decomposition 
        
        #NB: this metod doesn't 
        def get_PLU_decomposition(self):

        #solbe linear system

    Matrix.domain = domain
    return Matrix


"""solve system of linear eqyations
if there is no solution - return None.
If the system is undetermined (and hence there are more than one solutions) returns just one of them"""
def solve_lin_system_PLU_form(P, L, U, b):


def solve_lin_system(A, b):


