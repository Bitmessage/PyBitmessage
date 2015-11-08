UNAME_S := $(shell uname -s)
ifeq ($(UNAME_S),Darwin)
	CCFLAGS += -I/usr/local/Cellar/openssl/1.0.2d_1/include
	LDFLAGS += -L/usr/local/Cellar/openssl/1.0.2d_1/lib
endif
   	
all: bitmsghash.so

powtest:
	./testpow.py

bitmsghash.so: bitmsghash.o
	g++ bitmsghash.o -shared -fPIC -lpthread -lcrypto $(LDFLAGS) -o bitmsghash.so

bitmsghash.o:
	g++ -Wall -O3 -march=native -fPIC $(CCFLAGS) -c bitmsghash.cpp

clean:
	rm -f bitmsghash.o bitmsghash.so

