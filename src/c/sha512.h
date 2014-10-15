/* Taken from SHA512-based Unix crypt implementation.
   Released into the Public Domain by Ulrich Drepper <drepper@redhat.com>.  */

#include <stdint.h>
#include <string.h>

/* Structure to save state of computation between the single steps.  */
struct sha512_ctx
{
  uint64_t H[8];

  uint64_t total[2];
  uint64_t buflen;
  char buffer[256];	/* NB: always correctly aligned for uint64_t.  */
};

/* Initialize structure containing state of computation.
   (FIPS 180-2:5.3.3)  */
void
sha512_init_ctx (struct sha512_ctx *ctx);

/* Process the remaining bytes in the internal buffer and the usual
   prolog according to the standard and write the result to RESBUF.

   IMPORTANT: On some systems it is required that RESBUF is correctly
   aligned for a 32 bits value.  */
void *
sha512_finish_ctx (struct sha512_ctx *ctx, void *resbuf);

void
sha512_process_bytes (const void *buffer, size_t len, struct sha512_ctx *ctx);
