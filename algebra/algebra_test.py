print "Hello!"

from finite_field import *

F5 = FiniteField(5,1)

poly = multiivar_polynomialsOver(F5, 'X', 'Y', 'Z')


q = poly.from_string("1 - X * Y**2 * Z - 2 * Z**3 * X + 3")
print q 


f= q.evaluate([p_, p_, 3 ])


