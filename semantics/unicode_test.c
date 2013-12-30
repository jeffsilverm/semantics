/* This tests the ability of the UNIX system to handle unicode.
This program writes "Sarah" in Hebrew */

#include <stdio.h>
#define BUFFER_LEN 7

int main ( int argc, char *argv[] ) {

  char buffer[BUFFER_LEN];

  buffer[0]=0x05;
  buffer[1]=0xe1;
  buffer[2]=0x05;
  buffer[3]=0xe8;
  buffer[4]=0x05;
  buffer[5]=0xd4;
  buffer[6]=0;

  printf ("%s", buffer);
}

