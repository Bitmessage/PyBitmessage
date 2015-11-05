// bitmessage cracker, build with g++ or MSVS to a shared library, use included python code for usage under bitmessage
#ifdef _WIN32
#include "Winsock.h"
#include "Windows.h"
#define uint64_t unsigned __int64
#else
#include <arpa/inet.h>
#include <pthread.h>
#include <stdint.h>
#endif
#include <string.h>
#include <stdio.h>
#include <stdlib.h>

#include "openssl/sha.h"

#define HASH_SIZE 64
#define BUFLEN 16384

#define ntohll(x) ( ( (uint64_t)(ntohl( (unsigned int)((x << 32) >> 32) )) << 32) | ntohl( ((unsigned int)(x >> 32)) ) )

unsigned long long max_val;
unsigned char *initialHash;


int numthreads = 8;
unsigned long long successval = 0;
#ifdef _WIN32
DWORD WINAPI threadfunc(LPVOID lpParameter) {
	DWORD incamt = (DWORD)lpParameter;
#else
void * threadfunc(void* param) {
	unsigned int incamt = (unsigned int)param;
#endif
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
	return NULL;
}

extern "C" __declspec(dllexport) unsigned long long BitmessagePOW(unsigned char * starthash, unsigned long long target)
{
	successval = 0;
	max_val = target;
	initialHash = (unsigned char *)starthash;
#   ifdef _WIN32
	HANDLE* threads = (HANDLE*)calloc(sizeof(HANDLE), numthreads);
#   else
	pthread_t* threads = calloc(sizeof(pthread_t), numthreads);
#   endif
	for (int i = 0; i < numthreads; i++) {
#   ifdef _WIN32
		threads[i] = CreateThread(NULL, 0, threadfunc, (LPVOID)i, 0, NULL);
		SetThreadPriority(threads[i], THREAD_PRIORITY_IDLE);
#   else
		pthread_create(&threads[i], NULL, threadfunc, (void*)i);
#   endif
	}
#   ifdef _WIN32
	WaitForMultipleObjects(numthreads, threads, TRUE, INFINITE);
#   else
	for (int i = 0; i < numthreads; i++) {
		pthread_join(threads[i], NULL);
	}
#   endif
	free(threads);
	return successval;
}