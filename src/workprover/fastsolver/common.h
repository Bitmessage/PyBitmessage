#ifndef COMMON_H
    #define COMMON_H

    #ifdef _WIN32
        #define EXPORT __declspec(dllexport)
    #else
        #define EXPORT __attribute__ ((visibility("default")))
    #endif

    extern volatile int run;

    #define SEED_LENGTH (32 + 8)

    extern const char *initial_hash;
    extern unsigned long long target;
    extern const char *seed;

    int work(char *nonce, unsigned long long *iterations_count, size_t thread_number);
#endif
