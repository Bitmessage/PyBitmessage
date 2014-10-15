#include "sha512.h"
#include <stdint.h>

/*
 * 64-bit integer manipulation macros (big endian)
 */
#ifndef GET_UINT64_BE
#define GET_UINT64_BE(n,b,i)                            \
{                                                       \
    (n) = ( (uint64_t) (b)[(i)    ] << 56 )       \
        | ( (uint64_t) (b)[(i) + 1] << 48 )       \
        | ( (uint64_t) (b)[(i) + 2] << 40 )       \
        | ( (uint64_t) (b)[(i) + 3] << 32 )       \
        | ( (uint64_t) (b)[(i) + 4] << 24 )       \
        | ( (uint64_t) (b)[(i) + 5] << 16 )       \
        | ( (uint64_t) (b)[(i) + 6] <<  8 )       \
        | ( (uint64_t) (b)[(i) + 7]       );      \
}
#endif /* GET_UINT64_BE */

#ifndef PUT_UINT64_BE
#define PUT_UINT64_BE(n,b,i)                            \
{                                                       \
    (b)[(i)    ] = (unsigned char) ( (n) >> 56 );       \
    (b)[(i) + 1] = (unsigned char) ( (n) >> 48 );       \
    (b)[(i) + 2] = (unsigned char) ( (n) >> 40 );       \
    (b)[(i) + 3] = (unsigned char) ( (n) >> 32 );       \
    (b)[(i) + 4] = (unsigned char) ( (n) >> 24 );       \
    (b)[(i) + 5] = (unsigned char) ( (n) >> 16 );       \
    (b)[(i) + 6] = (unsigned char) ( (n) >>  8 );       \
    (b)[(i) + 7] = (unsigned char) ( (n)       );       \
}
#endif /* PUT_UINT64_BE */

void doPoW(uint64_t target, unsigned char initialHash[64], uint64_t* trialValue, uint64_t* nonce, unsigned int poolSize) {
	struct sha512_ctx ctx;
	unsigned char tmp[72];

	*trialValue = target + 1;

	while (*trialValue > target) {
		*nonce += poolSize;

		PUT_UINT64_BE(*nonce, tmp, 0);
		memcpy(&(tmp[8]), initialHash, 64);
			
		sha512_init_ctx(&ctx);
		sha512_process_bytes(tmp, 72, &ctx);
		sha512_finish_ctx(&ctx, tmp);

		sha512_init_ctx(&ctx);
		sha512_process_bytes(tmp, 64, &ctx);
		sha512_finish_ctx(&ctx, tmp);

		GET_UINT64_BE(*trialValue, tmp, 0);
	}
}

#ifdef TEST

#include <stdio.h>

int main() {
	uint64_t trialValue;
	uint64_t nonce = 0;
	unsigned char initialHash[64] = {
		0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
		0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 
		0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
		0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 
		0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 
		0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 
		0x00, 0x00, 0x00, 0x00 };
	uint64_t target = 9999999999999;

	doPoW(target, initialHash, &trialValue, &nonce, 1);
	if (nonce == 4284919Lu && trialValue == 6694291384049Lu) {
		printf("Test passed!\n");
	} else {
		printf("Test failed!\n");
		printf("Nonce == %lu\n", nonce);
		printf("trialValue == %lu\n", trialValue);
	}
	return 0;
}
#endif //TEST
