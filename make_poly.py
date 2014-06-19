#! /usr/bin/env python
#
# This program generates programs in FORTRAN and C that evaluate polynomials]
# using a "naive" calculation and using Horner's rule.
# A*x**2 + B*x + C = C + x * (B + A * (X)

import random
import subprocess
import timeit


def fortran_compile ( filename ):
   compile_command = ["gfortran", filename+".f", "-o", filename]
   print "The compile command is " + str(compile_command)
   return_code =  subprocess.call(compile_command)
   if return_code != 0 :
      raise subprocess.CalledProcessError

def fortran_execute ( filename, iterations ):
   execute_command = ["./"+filename, str(iterations)]
   print "The execute command is " + str(execute_command)
   return_code =  subprocess.call(execute_command)
   if return_code != 0 :
      raise subprocess.CalledProcessError
   
   


def make_fortran_naive( filename, coefficients, x, iterations ):

   with open(filename+".f", 'w') as f:
      num_coefs = len(coefficients)
      f.write("\tPROGRAM NAIVE\n"+\
              "\tREAL C(%d)\n" % num_coefs +\
              "\tCHARACTER(len=32) :: arg\n")
      for c in range(num_coefs) :
# FORTRAN arrays start at 1, but the range function starts at 0
         f.write("\tC(%d)=%f\n" % (c+1, coefficients[c]))
# See http://gcc.gnu.org/onlinedocs/gfortran/GETARG.html
      f.write("\tCALL getarg(1, arg)\n" +\
              "\tREAD (arg,*) ITERATIONS\n")
      
      f.write("\tX=%f\n" % x +\
              "\tDO 29999 K=0,ITERATIONS,1\n" +\
              "\t  Y=0.0\n"+\
              "\t  DO 21999 I=0,%d,1\n" % num_coefs +\
              "\t    Y=Y+C(I)*X**I\n" + \
              "21999\t  CONTINUE\n" + \
              "29999\tCONTINUE\n" +\
              "\tWRITE (*,*), Y\n" +\
              "\tEND\n")
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
      
      f.write("\tX=%f\n" % x +\
              "\tDO 29999 K=0,ITERATIONS,1\n" +\
              "\t  Y=0.0\n"+\
              "\t  DO 21999 I=0,%d,1\n" % num_coefs +\
              "\t    Y=C(I)+X*Y\n" + \
              "21999\t  CONTINUE\n" + \
              "29999\tCONTINUE\n" +\
              "\tWRITE (*,*), Y\n" +\
              "\tEND\n")
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
   print "The execute command is " + str(execute_command)
   return_code =  subprocess.call(execute_command)
   if return_code != 0 :
      raise subprocess.CalledProcessError


def make_c_horner( filename, coefficients, x, iterations ):
   with open(filename+".c", 'w') as f:
      num_coefs = len(coefficients)
      f.write("""#include <stdlib.h>
#include <stdio.h>
#include <math.h>
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
  y=0.0;
  for (i=0; i<%d; i++ ) {
    y=c[i]+x*y;
    }
  }
printf ("result is %%f\\n", y);
return 0;  
}""" % (x, num_coefs) )
   c_compile ( filename )
   print(str(timeit.timeit("c_execute('%s', %d)" % (filename, iterations), \
                       setup="from __main__ import c_execute", number=10))+" seconds")

             

def make_c_naive( filename, coefficients, x, iterations ):
   with open(filename+".c", 'w') as f:
      num_coefs = len(coefficients)
      f.write("""#include <stdlib.h>
#include <stdio.h>
#include <math.h>
int main(int argc, char *argv[] ){\n
double c[%d];\n
double x, y;
int i, k;
int iterations;\n"""  % num_coefs )
      for i in range(num_coefs):
         f.write("c[%d]=%f;\n" % (i, coefficients[i]))
      f.write("""
iterations = atoi(argv[1]);
x = %f;\n""" % x +\
"""for (k=0; k<iterations; k++ ) {
  y=0.0;
  for (i=0; i<%d; i++ ) {
/* Evidently, there is no built-in function for raising a double to an integer power
and I am too rushed to write one */\n""" % num_coefs + \
"""    y=y+c[i]*pow(x, (double) i);
    }
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

