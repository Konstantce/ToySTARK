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
                #in the case dim > 6 - find the determinant from the PLU decomposition 
                P, L, U = self.get_PLU_decomposition()
                sign = 1 if len(filter(lambda (x, y): x < y, itertools.combinations(P, 2))) % 2 == 0 else -1
                running_prod = self.domain(sign)
                for i in xrange(self.x_dim):
                    running_prod *= L[i][i] * U[i][i]
                return running_prod
                 
        def get_PLU_decomposition(self):
            #we use Dolittle algorithm with partial pivoting
            #NB: P is returning as a permutation vector - not matrix!
            assert(self.x_dim == self.y_dim, "PLU decomposition is defined only for square matrices.")
            dim = self.x_dim

            perms = []
            L = Matrix.zero_matrix(dim)
            for i in xrange(dim):
                L[i][i] = self.domain(1)
            U = Matrix(copy.deepcopy(self.data))

            for j in xrange(dim - 1):
                if U[j][j] == self.domain(0):
                    #find the first row with unzero element beneath U[j][j]
                    idx = next( (i for i in xrange(j+1, dim) if U[i][j] != self.domain(0)), None)
                    #if such row is found - just swap rows:
                    if idx is not None:
                        perms.append((j, idx))
                        for k in xrange(j, dim):
                            U[j][k], U[idx][k] = U[idx][k], U[j][k]
                        for k in xrange(j)
                            L[j][k], L[idx][k] = L[idx][k], L[j][k]

                #main reduction step
                if (U[j][j] != self.domain(0)):
                    for i in xrange(j+1, dim):
                        alpha = - U[i][j] / U[j][j]
                        L[i][j] = -alpha
                        U[i][j] = 0
                        for k in xrange(j+1, dim):
                            U[i][k] += alpha * U[j][k]

            #combine all permutations is permutation vector
            P = [x for x in xrange(dim)]
            for (pos1, pos2) in perms:
                P[pos1], P[pos2] = P[pos2], P[pos1]

            return P, L, U

        def get_dims(self):
            return self.x_dim, self.y_dim 
                
    Matrix.domain = domain
    return Matrix


"""solve quadratic system of linear eqyations
if there is no solution - return None.
If the system is undetermined (and hence there are more than one solutions) returns just one of them"""
def solve_lin_system_PLU_form(P, L, U, b):
    assert(L.get_dims()[0] == len(b), "Provided linear system is not quadratic.")
    dim = len(b)
    domain = b[0].__class__
    is_residue_field = hasattr(domain, "p") and not domain.is_extension_field

    #first pemute elements of B
    b = [b[i] for i in P]
    #solve Lx = b with forward propagation
    #here we use that there are only 1's on the diagonal of L
    x = []
    for i in xrange(dim):
        x_i = b[i] - sum([x[k] * L[i][k] for k in xrange(i)], domain(0))
        x.append(x_i)

    #solve Uy = x with backward propagation
    #As it is possible to have zeroes on the main diagonal - we apply iterative method,
    #which will work effectively only in the case of small residue finite domains and small number of diagonal zeroes
    #If our domain is not a residue finite field - we immediately throw an exception
    y = [domain(0)] * dim
    i = dim - 1
    break_points = []
    while i >= 0:
        if U[i][i] != domain(0):
            y[i] = (b[i] - sum([y[k] * U[i][k] for k in xrange(i+1, dim)], domain(0))) / U[i][i]
            i -= 1
        else:
            eq_check = (sum([y[k] * U[i][k] for k in xrange(i+1, dim)]) == b[i])
            if not break_points and not eq_check:
                #no solutions
                return None
            if not is_residue_field:
                raise StarkError("The system is undetermied: we unable to solbe it for now")
            if eq_check:
                break_points.append((i, 0))
                y[i] = domain(0)
                i -= 1
            else:
                #return to previous breakpoint
                idx = next( (i for i in xrange(len(break_points), -1, -1) if breakoints[i][1] != domain.p-1, None)
                if idx is None:
                    return None
                else:
                    breakpoints = breakpoints[:idx+1]
                    breakpoints[:-1][1] += 1
                    i, val = break_points[-1]
                    y[i] = val

    return y
                
        
def solve_lin_system(A, b):
    P, L, U = get_PLU_decomposition(A)
    return solve_lin_system_PLU_form(P, L, U, b)


