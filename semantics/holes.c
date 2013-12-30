/* This C program uses the lseek call to create a file that is full of holes */

#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <unistd.h>
#include <string.h>
#include <stdio.h>
#define BUFFER_LEN   200
#define WRITE_STR "This is a test\n"
#define WRITE_STR_LEN strlen(WRITE_STR)
#define DIAGNOSE_FAILURE(return_value, call)  if ( return_value < 0 ) { \
    errsave = errno; \
    decode_errno ( errsave ); \
    fprintf ( stderr, "%s failed in line %d\n", call, __LINE__ );\
    return 1;\
  };
#define NUM_HOLES 8

/* The kernel returns the reason why a syscall failed in errno */
#include <errno.h>

void decode_errno ( int errnum );

int main ( int argc, char *argv[] ) {

  int fd;          /* The file descriptor returned by creat or open syscalls */
  int status;      /* The status returned by syscalls that don't return an fd*/
  char buffer[BUFFER_LEN];   /* Place to put the bytes we read from the file */
  int errsave;     /* Needed to work around errno defined as a macro in errno.h */
  int i;

/*   int creat(const char *pathname, mode_t mode);
Returns a file descriptor, which is a small integer used for subsequent system service calls.  The first argument is the name of the file and the second
argument is the type of access, which is read/write.  
*/
  fd = creat( argv[1], O_RDWR );
  DIAGNOSE_FAILURE( fd, "creat" );
/* The second argument is the protection of the file, which is 0644 rw-r--r-- */
  status = fchmod ( fd, S_IRUSR | S_IWUSR | S_IRGRP | S_IROTH );
  DIAGNOSE_FAILURE( status, "fchmod");
  for (i=0; i<NUM_HOLES; i++ ) {
    status = write (fd, WRITE_STR, WRITE_STR_LEN );
    DIAGNOSE_FAILURE( status, "write");
    status = lseek(fd, i*50, SEEK_SET);
    DIAGNOSE_FAILURE( status, "lseek");
  };
  status = close( fd );
  DIAGNOSE_FAILURE( status, "close");
  fd = open( argv[1], O_RDONLY );
  DIAGNOSE_FAILURE( fd, "open");
  fprintf ( stderr, "Reading with lseek calls\n");
  for (i=0; i<NUM_HOLES; i++ ) {
    status = read (fd, buffer, BUFFER_LEN );
    DIAGNOSE_FAILURE( status, "read" );
    status = lseek(fd, i*50, SEEK_SET);
    DIAGNOSE_FAILURE( status, "lseek");
    if ( status < WRITE_STR_LEN ) {
      fprintf ( stderr, "The read call read only %d bytes but should have read %d\n",
      status, (int) WRITE_STR_LEN);
    };
    if ( strcmp( buffer, WRITE_STR ) == 0 ) {
      fprintf ( stderr, "Good comparison on the string written and read\n");
    } else {
      fprintf ( stderr, "ERROR: the string read in was %s while the string written out was %s\n", buffer, WRITE_STR );
    };
  };
  status = lseek(fd, 0, SEEK_SET);		/* rewind the file */
  DIAGNOSE_FAILURE( status, "lseek");
  fprintf ( stderr, "Reading without lseek calls\n");
  while ( 1 ) {
    status = read (fd, buffer, BUFFER_LEN );
    if ( status < 0 ) {
      DIAGNOSE_FAILURE( status, "read" );
    } else if ( status == 0 ) {
	fprintf ( stderr, "read returned 0 - EOF\n");
	break;
    } else if ( status < BUFFER_LEN ) {
	fprintf ( stderr, "Tried to read %d bytes but only read %d bytes\n", BUFFER_LEN, status );
    } else {
	fprintf ( stderr, "Good read\n");
    };
  };
  status = close(fd);
  DIAGNOSE_FAILURE( status, "close");
  fprintf ( stderr, "The program wrote %d bytes - how big is the file?  Use od -t x1 %s to find out\n",
	(int) ( WRITE_STR_LEN * NUM_HOLES ), argv[1] );
  return 0;
}
    



void decode_errno ( int errnum ) {

  char *err_mesg;  /* Points to the error message string returned by strerror*/
  
  err_mesg = strerror ( errnum );
  fprintf ( stderr, "Error from kernel is %s\n", err_mesg );
  return;
}

