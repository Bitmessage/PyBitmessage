#include <string.h>

#include <openssl/sha.h>

#include "common.h"

volatile int run;

const char *initial_hash;
unsigned long long target;
const char *seed;

static void encode_big_endian(char *result, unsigned long long number) {
    result[0] = number >> 56;
    result[1] = number >> 48 & 0xff;
    result[2] = number >> 40 & 0xff;
    result[3] = number >> 32 & 0xff;
    result[4] = number >> 24 & 0xff;
    result[5] = number >> 16 & 0xff;
    result[6] = number >> 8 & 0xff;
    result[7] = number & 0xff;
}

static unsigned long long decode_big_endian(const char *encoded) {
    return (
        (encoded[0] & 0xffull) << 56 |
        (encoded[1] & 0xffull) << 48 |
        (encoded[2] & 0xffull) << 40 |
        (encoded[3] & 0xffull) << 32 |
        (encoded[4] & 0xffull) << 24 |
        (encoded[5] & 0xffull) << 16 |
        (encoded[6] & 0xffull) << 8 |
        (encoded[7] & 0xffull)
    );
}

int work(char *nonce, unsigned long long *iterations_count, size_t thread_number) {
    unsigned long long i;

    char proof[8 + 64];
    char appended_seed[SEED_LENGTH + 8 + 8];

    memcpy(proof + 8, initial_hash, 64);
    memcpy(appended_seed, seed, SEED_LENGTH);
    encode_big_endian(appended_seed + SEED_LENGTH, thread_number);

    for (i = 0; run; ++i) {
        char randomness[64];

        size_t solutions_count = 0;
        char solutions[256];

        size_t j;

        encode_big_endian(appended_seed + SEED_LENGTH + 8, i);

        SHA512((unsigned char *) appended_seed, SEED_LENGTH + 8 + 8, (unsigned char *) randomness);

        memcpy(proof + 1, randomness, 7);

        for (j = 0; j < 256; ++j) {
            unsigned long long trial;

            SHA512_CTX context;

            char first_hash[64];
            char second_hash[64];

            proof[0] = j;

            SHA512_Init(&context);
            SHA512_Update(&context, (unsigned char *) proof, 8 + 64);
            SHA512_Final((unsigned char *) first_hash, &context);

            SHA512_Init(&context);
            SHA512_Update(&context, (unsigned char *) first_hash, 64);
            SHA512_Final((unsigned char *) second_hash, &context);

            trial = decode_big_endian(second_hash);

            if (trial <= target) {
                solutions[solutions_count] = j;
                ++solutions_count;
            }

            ++*iterations_count;
        }

        if (solutions_count != 0) {
            unsigned long long index = decode_big_endian(randomness + 7);

            nonce[0] = solutions[index % solutions_count];
            memcpy(nonce + 1, proof + 1, 7);

            return 1;
        }
    }

    return 0;
}
