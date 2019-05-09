// bitmessage cracker, build with g++ or MSVS to a shared library, use included python code for usage under bitmessage
#ifdef _WIN32
#include "winsock.h"
#include "windows.h"
#define uint64_t unsigned __int64
#else
#include <arpa/inet.h>
#include <pthread.h>
#include <stdint.h>
#endif
#include <string.h>
#include <stdio.h>
#include <stdlib.h>
#if defined(__APPLE__) || defined(__FreeBSD__) || defined (__DragonFly__) || defined (__OpenBSD__) || defined (__NetBSD__)
#include <sys/types.h>
#include <sys/sysctl.h>
#endif

#include "openssl/sha.h"

#define HASH_SIZE 64
#define BUFLEN 16384

#if defined(__GNUC__)
  #define EXPORT __attribute__ ((__visibility__("default")))
#elif defined(_WIN32)
  #define EXPORT __declspec(dllexport)
#endif

#ifndef __APPLE__
#define ntohll(x) ( ( (uint64_t)(ntohl( (unsigned int)((x << 32) >> 32) )) << 32) | ntohl( ((unsigned int)(x >> 32)) ) )
#endif

unsigned long long max_val;
unsigned char *initialHash;
unsigned long long successval = 0;
unsigned int numthreads = 0;

#ifdef _WIN32
DWORD WINAPI threadfunc(LPVOID param) {
#else
void * threadfunc(void* param) {
#endif
	unsigned int incamt = *((unsigned int*)param);
	SHA512_CTX sha;
	unsigned char buf[HASH_SIZE + sizeof(uint64_t)] = { 0 };
	unsigned char output[HASH_SIZE] = { 0 };

	memcpy(buf + sizeof(uint64_t), initialHash, HASH_SIZE);

	unsigned long long tmpnonce = incamt;
	unsigned long long * nonce = (unsigned long long *)buf;
	unsigned long long * hash = (unsigned long long *)output;
	while (successval == 0) {
		tmpnonce += numthreads;

		(*nonce) = ntohll(tmpnonce); /* increment nonce */
		SHA512_Init(&sha);
		SHA512_Update(&sha, buf, HASH_SIZE + sizeof(uint64_t));
		SHA512_Final(output, &sha);
		SHA512_Init(&sha);
		SHA512_Update(&sha, output, HASH_SIZE);
		SHA512_Final(output, &sha);

		if (ntohll(*hash) < max_val) {
			successval = tmpnonce;
		}
	}
#ifdef _WIN32
	return 0;
#else
	return NULL;
#endif
}

void getnumthreads()
{
#ifdef _WIN32
	DWORD_PTR dwProcessAffinity, dwSystemAffinity;
#elif __linux__
	// cpu_set_t dwProcessAffinity;
#elif __OpenBSD__
	int mib[2], core_count = 0;
	int dwProcessAffinity = 0;
	size_t len2;
#else
	int dwProcessAffinity = 0;
	int32_t core_count = 0;
#endif
	// size_t len = sizeof(dwProcessAffinity);
	// if (numthreads > 0)
	// 	return;
#ifdef _WIN32
	GetProcessAffinityMask(GetCurrentProcess(), &dwProcessAffinity, &dwSystemAffinity);
#elif __linux__
	// sched_getaffinity(0, len, &dwProcessAffinity);
#elif __OpenBSD__
	len2 = sizeof(core_count);
	mib[0] = CTL_HW;
	mib[1] = HW_NCPU;
	if (sysctl(mib, 2, &core_count, &len2, 0, 0) == 0)
		numthreads = core_count;
#else
	if (sysctlbyname("hw.logicalcpu", &core_count, &len, 0, 0) == 0)
		numthreads = core_count;
	else if (sysctlbyname("hw.ncpu", &core_count, &len, 0, 0) == 0)
		numthreads = core_count;
#endif
// 	for (unsigned int i = 0; i < len * 8; i++)
// #if defined(_WIN32)
// #if defined(_MSC_VER)
// 		if (dwProcessAffinity & (1i64 << i))
// #else // CYGWIN/MINGW
// 		if (dwProcessAffinity & (1ULL << i))
// #endif
// #elif defined __linux__
// 		if (CPU_ISSET(i, &dwProcessAffinity))
// #else
// 		if (dwProcessAffinity & (1 << i))
// #endif
// 			numthreads++;
// 	if (numthreads == 0) // something failed
// 		numthreads = 1;
// 	printf("Number of threads: %i\n", (int)numthreads);
}

extern "C" EXPORT unsigned long long BitmessagePOW(unsigned char * starthash, unsigned long long target)
{
	successval = 0;
	max_val = target;
	getnumthreads();
	initialHash = (unsigned char *)starthash;
#   ifdef _WIN32
	HANDLE* threads = (HANDLE*)calloc(sizeof(HANDLE), numthreads);
#   else
	pthread_t* threads = (pthread_t*)calloc(sizeof(pthread_t), numthreads);
	struct sched_param schparam;
	schparam.sched_priority = 0;
#   endif
	unsigned int *threaddata = (unsigned int *)calloc(sizeof(unsigned int), numthreads);
	for (unsigned int i = 0; i < numthreads; i++) {
		threaddata[i] = i;
#   ifdef _WIN32
		threads[i] = CreateThread(NULL, 0, threadfunc, (LPVOID)&threaddata[i], 0, NULL);
		SetThreadPriority(threads[i], THREAD_PRIORITY_IDLE);
#   else
		pthread_create(&threads[i], NULL, threadfunc, (void*)&threaddata[i]);
#   ifdef __linux__
		pthread_setschedparam(threads[i], 0, &schparam);
#   else
		pthread_setschedparam(threads[i], SCHED_RR, &schparam);
#   endif
#   endif
	}
#   ifdef _WIN32
	WaitForMultipleObjects(numthreads, threads, TRUE, INFINITE);
#   else
	for (unsigned int i = 0; i < numthreads; i++) {
		pthread_join(threads[i], NULL);
	}
#   endif
	free(threads);
	free(threaddata);
	return successval;
}
