#! /usr/bin/env python
#
# This program generates programs in FORTRAN and C that evaluate polynomials]
# using a "naive" calculation and using Horner's rule.
# A*x**2 + B*x + C = C + x * (B + A * (X)

import random
import subprocess
import timeit
from efficient_exponent import efficient_exponent


def fortran_compile ( filename ):
# fixed-line-length=none means that a line can be as long as it needs to be.
   compile_command = ["gfortran", filename+".f", "-ffixed-line-length-none", "-o", filename]
   print "The compile command is " + str(compile_command)
   return_code =  subprocess.call(compile_command)
   if return_code != 0 :
      raise subprocess.CalledProcessError

def fortran_execute ( filename, iterations ):
   execute_command = ["./"+filename, str(iterations)]
#   print "The execute command is " + str(execute_command)
   return_code =  subprocess.call(execute_command)
   if return_code != 0 :
      raise subprocess.CalledProcessError
   
   


def make_fortran_naive( filename, coefficients, x, iterations ):

   with open(filename+".f", 'w') as f:
      num_coefs = len(coefficients)
      f.write("\tPROGRAM NAIVE\n"+\
              "\tREAL C(%d)\n" % num_coefs +\
              "\tDOUBLE PRECISION X, Y\n" +\
              "\tCHARACTER(len=32) :: arg\n")
      for c in range(num_coefs) :
# FORTRAN arrays start at 1, but the range function starts at 0
         f.write("\tC(%d)=%f\n" % (c+1, coefficients[c]))
# See http://gcc.gnu.org/onlinedocs/gfortran/GETARG.html
      f.write("\tCALL getarg(1, arg)\n" +\
              "\tREAD (arg,*) ITERATIONS\n")
      
#      f.write("\tX=%f\n" % x +\
#              "\tDO 29999 K=0,ITERATIONS,1\n" +\
#              "\t  Y=0.0\n" +\
#              "\t  DO 21999 I=0,%d,1\n" % num_coefs +\
#              "\t    Y=Y+C(I)*X**I\n" + \
#              "21999\t  CONTINUE\n" + \
#              "29999\tCONTINUE\n" +\
#              "\tWRITE (*,*), Y\n" +\
#              "\tEND\n")
      f.write("""
\tX=%f
\tDO 29999 K=0,ITERATIONS,1
\t  Y=C(1)""" % x )
      for i in range(1,num_coefs) :
         f.write("+C(%d)*X**%d" % (i+1, i) )
      f.write("""
21999\t  CONTINUE
29999\tCONTINUE
\tWRITE (*,*), Y
\tEND\n""")

   fortran_compile ( filename )
   print(str(timeit.timeit("fortran_execute('%s', %d)" % (filename, iterations), \
                       setup="from __main__ import fortran_execute", number=10))+" seconds")
   
     
def make_fortran_horner( filename, coefficients, x, iterations ):
   with open(filename+".f", 'w') as f:
      num_coefs = len(coefficients)
      f.write("\tPROGRAM HORNER\n"+\
              "\tDOUBLE PRECISION C(%d)\n" % num_coefs +\
              "\tDOUBLE PRECISION X, Y\n" +\
              "\tCHARACTER(len=32) :: arg\n")
      for c in range(num_coefs) :
# FORTRAN arrays start at 1, but the range function starts at 0
         f.write("\tC(%d)=%f\n" % (c+1, coefficients[c]))
# See http://gcc.gnu.org/onlinedocs/gfortran/GETARG.html
      f.write("\tCALL getarg(1, arg)\n" +\
              "\tREAD (arg,*) ITERATIONS\n")
      
      f.write("""
\tX=%f
\tDO 29999 K=0,ITERATIONS,1
\t  Y="""  % x )
      for i in range(num_coefs) :
         if i == num_coefs - 1 :
            f.write("C(%d)" % (i+1) )
         else :
            f.write("(C(%d)+X*" % (i+1) )
      for i in range(1,num_coefs) :
         f.write(")")
      f.write("""
29999\tCONTINUE
\tWRITE (*,*), Y
\tEND\n""")
   fortran_compile ( filename )
   print(str(timeit.timeit("fortran_execute('%s', %d)" % (filename, iterations), \
                       setup="from __main__ import fortran_execute", number=10))+" seconds")


def c_compile ( filename ):
   compile_command = ["gcc", filename+".c", "-o", filename, "-lm"]
   print "The compile command is " + str(compile_command)
   return_code =  subprocess.call(compile_command)
   if return_code != 0 :
      raise subprocess.CalledProcessError

def c_execute ( filename, iterations ):
   execute_command = ["./"+filename, str(iterations)]
#   print "The execute command is " + str(execute_command)
   return_code =  subprocess.call(execute_command)
   if return_code != 0 :
      raise subprocess.CalledProcessError


def make_c_horner( filename, coefficients, x, iterations ):
   with open(filename+".c", 'w') as f:
      num_coefs = len(coefficients)
      f.write("""#include <stdlib.h>
#include <stdio.h>
int main(int argc, char *argv[] ){\n
double c[%d];\n
double x, y;
int i, k;
int iterations;\n"""  % num_coefs )
      for i in range(num_coefs):
         f.write("c[%d]=%f;\n" % (i, coefficients[i]))
      f.write("""
iterations = atoi(argv[1]);
x = %f;
for (k=0; k<iterations; k++ ) {
  y=(""" % x)
      for i in range(num_coefs):
         if i == num_coefs -1 :
            f.write("c[%d]" % i)
         else:
            f.write("c[%d]+x*(" % i )
      f.write(")"*num_coefs)
      f.write(""";
  }
printf ("result is %f\\n", y);
return 0;  
}""" )
   c_compile ( filename )
   print(str(timeit.timeit("c_execute('%s', %d)" % (filename, iterations), \
                       setup="from __main__ import c_execute", number=10))+" seconds")

             

def make_c_naive( filename, coefficients, x, iterations ):
   with open(filename+".c", 'w') as f:
      num_coefs = len(coefficients)
      f.write("""#include <stdlib.h>
#include <stdio.h>

/* C doesn't have a function that raises a double number to an integer power.
It has pow, which uses 2 infinite series, and increased execution time by a
factor of 8 */
double powi( double x, int i ){
  double r;
  int k;
  r = 1.0;
  for (k=0; k<i; k++ ){
    r *= x;
  }
  return r;
}

int main(int argc, char *argv[] ){\n
double c[%d];\n
double x, y;
int i, k;
int iterations;\n"""  % num_coefs )
      for i in range(num_coefs):
         f.write("c[%d]=%f;\n" % (i, coefficients[i]))
      f.write("""
iterations = atoi(argv[1]);
x = %f;
for (k=0; k<iterations; k++ ) {
  y=c[0] +""" % x)
      for i in range(1,num_coefs) :
         if i < num_coefs-1 :
            f.write(("c[%d]*" % i ) + efficient_exponent(i,'x')+" + ")
         else :
            f.write(("c[%d]*" % i ) + efficient_exponent(i,'x')+";" )
      f.write("""
    }
printf ("result is %f\\n", y);
return 0;  
}""" )
   c_compile ( filename )
   print(str(timeit.timeit("c_execute('%s', %d)" % (filename, iterations), \
                       setup="from __main__ import c_execute", number=10))+" seconds")

             


if __name__ == "__main__" :
   order = int( raw_input("Enter the order of the polynomial "))
   iterations = int ( raw_input("Enter the number of iterations (20000000 is a good start) "))

   coefficients = []

   for i in range(order):
      coefficients.append( random.random() )

   make_fortran_naive( "naive_fortran", coefficients, 1.0, iterations )

   make_fortran_horner("horner_fortran", coefficients, 1.0, iterations )

   make_c_naive ("naive_c", coefficients, 1.0, iterations )

   make_c_horner ("horner_c", coefficients, 1.0, iterations )

