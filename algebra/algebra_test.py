print "Hello!"

from finite_field import *

F5 = FiniteField(5,1)

poly = multiivar_polynomialsOver(F5, 'X', 'Y', 'Z')


q = poly.domain.init_from_subdomain(3, True)
print q 


#print q.evaluate([7, p_])
#print isinstance(p_, Placeholder)