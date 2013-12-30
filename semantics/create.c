/* Create.c - demonstration of the creat system service call */
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <unistd.h>
#include <string.h>
#include <stdio.h>
#define BUFFER_LEN   2000
#define WRITE_STR "This is a test\n"
#define WRITE_STR_LEN strlen(WRITE_STR)
#define DIAGNOSE_FAILURE(return_value, call)  if ( return_value < 0 ) { \
    errsave = errno; \
    decode_errno ( errsave ); \
    fprintf ( stderr, "%s failed in line %d\n", call, __LINE__ );\
    return 1;\
  };

/* The kernel returns the reason why a syscall failed in errno */
#include <errno.h>

void decode_errno ( int errnum );

int main ( int argc, char *argv[] ) {
  
  int fd;          /* The file descriptor returned by creat or open syscalls */
  int status;      /* The status returned by syscalls that don't return an fd*/
  char buffer[BUFFER_LEN];   /* Place to put the bytes we read from the file */
  int errsave;     /* Needed to work around errno defined as a macro in errno.h */

/*   int creat(const char *pathname, mode_t mode);
Returns a file descriptor, which is a small integer used for subsequent system service calls.  The first argument is the name of the file and the second
argument is the type of access, which is read/write.  
*/
  fd = creat( argv[1], O_RDWR );
  DIAGNOSE_FAILURE( fd, "creat" );
/* The second argument is the protection of the file, which is 0644 rw-r--r-- */
  status = fchmod ( fd, S_IRUSR | S_IWUSR | S_IRGRP | S_IROTH );
  DIAGNOSE_FAILURE( status, "fchmod");
  status = write (fd, WRITE_STR, WRITE_STR_LEN );
  DIAGNOSE_FAILURE( status, "write");
#if 1==2
  status = lseek(fd, SEEK_SET, 0 );
  DIAGNOSE_FAILURE( status, "lseek");
#else
  status = close( fd );
  DIAGNOSE_FAILURE( status, "close");
  fd = open( argv[1], O_RDONLY );
  DIAGNOSE_FAILURE( fd, "open");
#endif
  status = read (fd, buffer, BUFFER_LEN );
  DIAGNOSE_FAILURE( status, "read" );
  if ( status < WRITE_STR_LEN ) {
    fprintf ( stderr, "The read call read only %d bytes but should have read %d\n",
    status, (int) WRITE_STR_LEN);
  };
  if ( strcmp( buffer, WRITE_STR ) == 0 ) {
    fprintf ( stderr, "Good comparison on the string written and read\n");
  } else {
    fprintf ( stderr, "ERROR: the string read in was %s while the string written out was %s\n", buffer, WRITE_STR );
  };
  status = close(fd);
  DIAGNOSE_FAILURE( status, "close");
  return 0;
}

void decode_errno ( int errnum ) {

  char *err_mesg;  /* Points to the error message string returned by strerror*/
  
  err_mesg = strerror ( errnum );
  fprintf ( stderr, "Error from kernel is %s\n", err_mesg );
  return;
}
  
 
