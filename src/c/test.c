#include <stdint.h>

//Raise this here and in cwrapper.py when making incompatible changes in the lib
#define LIBRARYVERSION 1

//Decrease this here and in cwrapper.py after porting the lib to a now architecture
#define UNSUPPORTED -1 

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

int test() {
	/* Test if we are on a big endian machine 
	 * since others are not supported at the moment. 
	 * If that's the case, n should be  
	 * {0x00, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07} 
	 * after PUT_UINT64_BE(). */

	uint64_t i = 283686952306183Lu;
	unsigned char x[8];
	
	PUT_UINT64_BE(i, x, 0);

	int n;
	for (n=0;n<8;++n) {
		if (x[n] != n) return UNSUPPORTED;
	}

	return LIBRARYVERSION;
}

#ifdef TEST

#include <stdio.h>

int main() {
	switch(test()) {
		case LIBRARYVERSION:
			printf("Test passed if you are on a BIG ENDIAN ENGINE\n");
			break;
		case UNSUPPORTED:
			printf("Test passed of you are NOT on a BIG ENDIAN ENGINE!\n");
		default:
			printf("Test failed!\n");
			break;
	}
	return 0;
}
#endif //TEST
