print "Hello!"

from finite_field import *

F5 = FiniteField(5,1)

a = F5(7)
b = F5(1)
print a+b


polysMod5 = polynomialsOver(F5, 'X')
poly = polynomialsOver(polysMod5, 'Y')

q = poly.from_string("X**2 + Y")
print q.evaluate([7, p_])
print isinstance(p_, Placeholder)