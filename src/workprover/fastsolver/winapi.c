#include <string.h>

#include <Windows.h>

#include "common.h"

static int initialized;

#define MAXIMUM_THREADS_COUNT 4096

static size_t threads_count;
static HANDLE threads[MAXIMUM_THREADS_COUNT];

static CRITICAL_SECTION lock;
static CONDITION_VARIABLE start = CONDITION_VARIABLE_INIT;
static CONDITION_VARIABLE done = CONDITION_VARIABLE_INIT;

static size_t running_threads_count;

static int found;
static char best_nonce[8];
static unsigned long long total_iterations_count;

DWORD WINAPI thread_function(LPVOID argument) {
    size_t thread_number = (HANDLE *) argument - threads;

    while (1) {
        char nonce[8];
        unsigned long long iterations_count = 0;
        int result;

        EnterCriticalSection(&lock);

        while (!run && threads_count > thread_number) {
            SleepConditionVariableCS(&start, &lock, INFINITE);
        }

        if (threads_count <= thread_number) {
            LeaveCriticalSection(&lock);

            return 0;
        }

        ++running_threads_count;

        LeaveCriticalSection(&lock);

        result = work(nonce, &iterations_count, thread_number);

        EnterCriticalSection(&lock);

        if (result == 1) {
            found = 1;
            memcpy(best_nonce, nonce, 8);
        }

        total_iterations_count += iterations_count;

        run = 0;
        --running_threads_count;

        WakeConditionVariable(&done);
        LeaveCriticalSection(&lock);
    }
}

static int initialize(void) {
    if (initialized == 1) {
        return 1;
    }

    InitializeCriticalSection(&lock);

    initialized = 1;

    return 1;
}

EXPORT size_t fastsolver_add(void) {
    if (initialize() == 0) {
        return threads_count;
    }

    EnterCriticalSection(&lock);

    threads[threads_count] = CreateThread(NULL, 0, thread_function, &threads[threads_count], 0, NULL);

    if (threads[threads_count] == NULL) {
        LeaveCriticalSection(&lock);

        return threads_count;
    }

    SetThreadPriority(threads[threads_count], THREAD_PRIORITY_IDLE);

    ++threads_count;

    LeaveCriticalSection(&lock);

    return threads_count;
}

EXPORT size_t fastsolver_remove(size_t count) {
    size_t i;

    EnterCriticalSection(&lock);

    threads_count -= count;

    WakeAllConditionVariable(&start);
    LeaveCriticalSection(&lock);

    WaitForMultipleObjects(count, threads + threads_count, TRUE, INFINITE);

    for (i = 0; i < count; ++i) {
        CloseHandle(threads[threads_count + i]);
    }

    return threads_count;
}

EXPORT int fastsolver_search(
    char *local_nonce,
    unsigned long long *local_iterations_count,
    const char *local_initial_hash,
    unsigned long long local_target,
    const char *local_seed,
    unsigned long long timeout
) {
    initial_hash = local_initial_hash;
    target = local_target;
    seed = local_seed;

    found = 0;
    total_iterations_count = 0;

    EnterCriticalSection(&lock);

    run = 1;

    WakeAllConditionVariable(&start);

    SleepConditionVariableCS(&done, &lock, timeout / 1000);

    run = 0;

    while (running_threads_count != 0) {
        SleepConditionVariableCS(&done, &lock, INFINITE);
    }

    LeaveCriticalSection(&lock);

    if (found) {
        memcpy(local_nonce, best_nonce, 8);
    }

    *local_iterations_count = total_iterations_count;

    return found;
}
