from algebra.polynomials import * 
from utils.utils import *

import inspect

class AIR():
    # w - register width, T - trace length; field = used base_field
    def __init__(self, w, T, field):
        #here we need to say, what does it mean to be a trace constraint
        self.w = w
        self.T = T
        self.field = field
        self.boundary_constraints = []
        self.trace_constraints = []
        self.vars = ['X' + str(i) for i in xrange(1, w+1)] + ['Y' + str(i) for i in xrange(1, w+1)]
        self.poly_ring = multiivar_polynomialsOver(field, *self.vars)
        self.witness = None
        self.boolean_circuit = (lambda: True)

    def set_witness(self, witness):
        self.witness = witness

    def set_circuit(self, circuit):
        assert callable(circuit), "provided circuit is not a funciton"
        self.boolean_circuit = circuit
    
    # boundary constraints are of the form (i, j, val), where 
    # i - number of step in trace from 0 to T
    # j - number of register from o to w
    # val - concrete value from field
    def add_boundary_constraint(self, i, j, val):
        assert (0 <= i < self.T), "specified value doesn't point to any correct step in execution trace"
        assert (0 <= j < self.w), "specified value  is not a register index" 
        self.boundary_constraints.append((i, j, self.field(val)))
    
    # trace constraints are of the form (i, poly), where
    # i - is the number of execution step
    # poly - polynomial in variables X1, .. X_w, Y_1, .. Y_w connecting registers between step i and i+1
    def add_trace_constraint(self, poly):
        self.trace_constraints.append(poly)

    # check if all constraints are defined at each execution step
    def consistency_check(self):
        if len(self.trace_constraints) != len(inspect.getargspec(self.boolean_circuit).args):
            return False
        if self.witness:
            return self.witness_check()
        return True
    
    # check if provided witness satisfies all of the constraints
    # witness should be 2-dimensional matrix of size [T][w] 
    def witness_check(self):
        assert self.witness is not None, "Witness is not set."
        for i, j, val in self.boundary_constraints:
            if self.witness[i][j] != val:
                return False

        for i in xrange(self.T-1):
            #TODO: get Rid of deepcopy here
            args = [self.poly_ring(poly).evaluate((self.witness[i] + self.witness[i+1])) == 0 for poly in self.trace_constraints]
            if not self.boolean_circuit(*args):
                return False
        return True



