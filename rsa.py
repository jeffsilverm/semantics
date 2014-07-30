#!/usr/bin/env python
 
# This example demonstrates RSA public-key cryptography in an
# easy-to-follow manner. It works on integers alone, and uses much smaller numbers
# for the sake of clarity. 
 
from random import randint
 
 
#####################################################################
# Next, some functions we'll need in a moment:
#####################################################################
# Note on what these operators do:
# %  is the modulus (remainder) operator: 10 % 3 is 1
# // is integer (round-down) division: 10 // 3 is 3
# ** is exponent (2**3 is 2 to the 3rd power)
 
# Brute-force (i.e. try every possibility) primality test.
def is_prime(x):
    if x%2==0 and x>2: return False     # False for all even numbers
    i=3                                 # we don't divide by 1 or 2
    sqrt=x**.5                          
    while i<sqrt:
        if x%i==0: return False
        i+=2
    return True
 
# Part of find_inverse below
# See: http://en.wikipedia.org/wiki/Extended_Euclidean_algorithm
def eea(a,b):
    if b==0:
        return (1,0)
    (q,r) = (a//b,a%b)
    (s,t) = eea(b,r)
    return (t, s-(q*t) )
 
# Find the multiplicative inverse of x (mod y)
# see: http://en.wikipedia.org/wiki/Modular_multiplicative_inverse
def find_inverse(x,y):
    inv = eea(x,y)[0]
    if inv < 1: inv += y #we only want positive values
    return inv

def make_random_prime_int(n,b):
    """This function returns a random prime number"""

    while True :
# This is for illustrative purposes only.  Do not use randint for security
# purposes.  Use os.urandom or SystemRandom if you want cryptographically
# secure random numbers.
# Return a random integer N such that a <= N <= b.
        c = randint(n,b)
        if is_prime(c) :
            return c


#####################################################################
# pick some random prime numbers
#####################################################################
while True:
    P = make_random_prime_int(65537,300000)
    Q = make_random_prime_int(65537,300000)
    if P != Q:
        break
#E = 45231   # usually a constant
# E=53   # from the original program
E=65537   # From a real cert
# P=97   #
# P=65539
# Q=83

 
#####################################################################
# Make sure the numbers we picked above are valid.
#####################################################################
 
if not is_prime(P):
    raise AssertionError ("P (%i) is not prime" % P)
if not is_prime(Q):
    raise AssertionError ("Q (%i) is not prime" % Q)
 
T=(P-1)*(Q-1) # Euler's totient (intermediate result)
# Assuming E is prime, we just have to check against T
if E<1 or E > T:
    raise AssertionError("1 < E < T is false.  E=%d T=%d" % (E, T) )
if T%E==0:
    raise AssertionError("E is not coprime with T")
 
#####################################################################
# Now that we've validated our random numbers, we derive our keys.
#####################################################################
 
# Product of P and Q is our modulus; the part determines as the "key size".
MOD=P*Q
 
# Private exponent is inverse of public exponent with respect to (mod T)
D = find_inverse(E,T)
 
# The modulus is always needed, while either E or D is the exponent, depending on 
# which key we're using. D is much harder for an adversary to derive, so we call
# that one the "private" key.
 
print "public key: (MOD: %i, E: %i)" % (MOD,E)
print "private key: (MOD: %i, D: %i)" % (MOD,D)
 
# Note that P, Q, and T can now be discarded, but they're usually
# kept around so that a more efficient encryption algorithm can be used.
# http://en.wikipedia.org/wiki/RSA#Using_the_Chinese_remainder_algorithm
 
#####################################################################
# We have our keys, let's do some encryption
#####################################################################
 
# Here I only focus on whether you're applying the private key or 
# applying the public key, since either one will reverse the other. 
 

print "Enter \">NUMBER\" to apply private key and \"<NUMBER\" to apply public key; \"Q\" to quit."
while True:
    line=raw_input("? ")
    if not line: break
    if line=='q' or line=='Q':
        break
    
    if line[0]=='<':
        key = E
    elif line[0]=='>':
        key = D
    else:
        print "Must start with either < or >"
        print "Enter \">NUMBER\" to apply private key and \"<NUMBER\" to apply public key; \"Q\" to quit."
        continue
    
    line=line[1:]
    try:
        before=int(line)
    except ValueError:
        print "not a number: \"%s\"" % (line)
        print "Enter \">NUMBER\" to apply private key and \"<NUMBER\" to apply public key; \"Q\" to quit."
        continue
 
    if before >= MOD:
        print "Only values up to %i can be encoded with this key (choose bigger primes next time)" % (MOD,)
        continue
 
    # Note that the pow() built-in does modulo exponentation. That's handy, since it saves us having to
    # implement that ablity.
    # http://en.wikipedia.org/wiki/Modular_exponentiation
 
    after = pow(before,key,MOD) #encrypt/decrypt using this ONE function. Surprisingly simple.
 
    if key == D:
        print "PRIVATE(%i) >>  %i" %(before,after)
    else:
        print "PUBLIC(%i) >>  %i" %(before,after)
