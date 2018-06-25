#include <string.h>
#include <time.h>

#include <pthread.h>

#include "common.h"

static int initialized;

#define MAXIMUM_THREADS_COUNT 4096

static size_t threads_count;
static pthread_t threads[MAXIMUM_THREADS_COUNT];

static pthread_mutex_t lock;
static pthread_cond_t start;
static pthread_cond_t done;

static size_t running_threads_count;

static int found;
static char best_nonce[8];
static unsigned long long total_iterations_count;

static void *thread_function(void *argument) {
    size_t thread_number = (pthread_t *) argument - threads;

    while (1) {
        char nonce[8];
        unsigned long long iterations_count = 0;
        int result;

        pthread_mutex_lock(&lock);

        while (!run && threads_count > thread_number) {
            pthread_cond_wait(&start, &lock);
        }

        if (threads_count <= thread_number) {
            pthread_mutex_unlock(&lock);

            return NULL;
        }

        ++running_threads_count;

        pthread_mutex_unlock(&lock);

        result = work(nonce, &iterations_count, thread_number);

        pthread_mutex_lock(&lock);

        if (result == 1) {
            found = 1;
            memcpy(best_nonce, nonce, 8);
        }

        total_iterations_count += iterations_count;

        run = 0;
        --running_threads_count;

        pthread_cond_signal(&done);
        pthread_mutex_unlock(&lock);
    }
}

static int initialize(void) {
    pthread_condattr_t done_attributes;

    if (initialized == 1) {
        return 1;
    }

    if (pthread_mutex_init(&lock, NULL) != 0) {
        goto error_lock;
    }

    if (pthread_cond_init(&start, NULL) != 0) {
        goto error_start;
    }

    if (pthread_condattr_init(&done_attributes) != 0) {
        goto error_done_attributes;
    }

    #ifndef __APPLE__
        pthread_condattr_setclock(&done_attributes, CLOCK_MONOTONIC);
    #endif

    if (pthread_cond_init(&done, &done_attributes) != 0) {
        goto error_done;
    }

    pthread_condattr_destroy(&done_attributes);

    initialized = 1;

    return 1;

    error_done: pthread_condattr_destroy(&done_attributes);
    error_done_attributes: pthread_cond_destroy(&start);
    error_start: pthread_mutex_destroy(&lock);
    error_lock: return 0;
}

EXPORT size_t fastsolver_add(void) {
    #ifdef SCHED_IDLE
        int policy = SCHED_IDLE;
    #else
        int policy = SCHED_OTHER;
    #endif

    struct sched_param parameters;

    if (initialize() == 0) {
        return threads_count;
    }

    pthread_mutex_lock(&lock);

    if (pthread_create(&threads[threads_count], NULL, thread_function, &threads[threads_count]) != 0) {
        pthread_mutex_unlock(&lock);

        return threads_count;
    }

    parameters.sched_priority = sched_get_priority_min(policy);
    pthread_setschedparam(threads[threads_count], policy, &parameters);

    ++threads_count;

    pthread_mutex_unlock(&lock);

    return threads_count;
}

EXPORT size_t fastsolver_remove(size_t count) {
    size_t i;

    pthread_mutex_lock(&lock);

    threads_count -= count;

    pthread_cond_broadcast(&start);
    pthread_mutex_unlock(&lock);

    for (i = 0; i < count; ++i) {
        void *result;

        pthread_join(threads[threads_count + i], &result);
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
    struct timespec wait_time;
    unsigned long long nanoseconds;

    initial_hash = local_initial_hash;
    target = local_target;
    seed = local_seed;

    found = 0;
    total_iterations_count = 0;

    #ifdef __APPLE__
        wait_time.tv_sec = 0;
        wait_time.tv_nsec = 0;
    #else
        clock_gettime(CLOCK_MONOTONIC, &wait_time);
    #endif

    nanoseconds = wait_time.tv_nsec + timeout;

    wait_time.tv_sec += nanoseconds / 1000000000;
    wait_time.tv_nsec = nanoseconds % 1000000000;

    pthread_mutex_lock(&lock);

    run = 1;

    pthread_cond_broadcast(&start);

    #ifdef __APPLE__
        pthread_cond_timedwait_relative_np(&done, &lock, &wait_time);
    #else
        pthread_cond_timedwait(&done, &lock, &wait_time);
    #endif

    run = 0;

    while (running_threads_count != 0) {
        pthread_cond_wait(&done, &lock);
    }

    pthread_mutex_unlock(&lock);

    if (found) {
        memcpy(local_nonce, best_nonce, 8);
    }

    *local_iterations_count = total_iterations_count;

    return found;
}
