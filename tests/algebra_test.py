print "Hello!"

import sys
from os import path
sys.path.append( path.dirname( path.dirname( path.abspath(__file__) ) ) )

print path.dirname(path.dirname(path.abspath(__file__)))

from algebra.finite_field import *

F5 = FiniteField(5,1)

poly = multiivar_polynomialsOver(F5, 'X', 'Y', 'Z')


q = poly.from_string("1 - X * Y**2 * Z - 2 * Z**3 * X + 3")
print q 


f= q.evaluate([p_, p_, 3 ])
print f
print type(f)
#print isinstance(p_, Placeholder)