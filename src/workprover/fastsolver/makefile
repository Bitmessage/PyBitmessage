CFLAGS += -std=gnu99 -Wall -Wextra -pedantic -O3 -fPIC -fvisibility=hidden
LDFLAGS += -shared
LDLIBS = -lpthread -lcrypto

libfastsolver.so: common.o pthread.o
	$(CC) $(LDFLAGS) -o $@ common.o pthread.o $(LDLIBS)

common.o: common.h common.c
pthread.o: common.h pthread.c

clean:
	rm -f common.o pthread.o libfastsolver.so
