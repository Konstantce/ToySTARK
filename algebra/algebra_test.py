print "Hello!"

from finite_field import *

F5 = FiniteField(5,1)

poly = multiivar_polynomialsOver(F5, 'X', 'Y', 'Z')


q = poly.from_string("1 - X * Y**2 * Z - 2 * Z**3 * X + 3")
print q 


f= q.evaluate([p_, p_, 3 ])
print f
print type(f)
#print isinstance(p_, Placeholder)

frame = b'\xff\xff\xff\xffXabccc'
zzz = [ord(x) for x in frame]
print zzz

l = [1,2,3,4,5]
l2 = l[::-2]
print l2

import itertools
basis = [-1, -1, -1]
#y = (sum(map(lambda (i,n): n**i, enumerate(x))) for x in itertools.product(xrange(3), repeat = 3))
y = (reduce((lambda c, (i,y): c + basis[i] * y), enumerate(x), 0) for x in itertools.product(xrange(3), repeat = 3))
for x in y:
    print x

