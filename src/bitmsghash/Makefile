UNAME_S := $(shell uname -s)
ifeq ($(UNAME_S),Darwin)
	CCFLAGS += -I/usr/local/opt/openssl/include
	LDFLAGS += -L/usr/local/opt/openssl/lib
else ifeq ($(UNAME_S),MINGW32_NT-6.1)
	CCFLAGS += -IC:\OpenSSL-1.0.2j-mingw\include -D_WIN32 -march=native
	LDFLAGS += -static-libgcc -LC:\OpenSSL-1.0.2j-mingw\lib -lwsock32 -o bitmsghash32.dll -Wl,--out-implib,bitmsghash.a
else
	LDFLAGS += -lpthread -o bitmsghash.so
endif

all: bitmsghash.so

powtest:
	./testpow.py

bitmsghash.so: bitmsghash.o
	${CXX} bitmsghash.o -shared -fPIC -lcrypto $(LDFLAGS)

bitmsghash.o:
	${CXX} -Wall -O3 -march=native -fPIC $(CCFLAGS) -c bitmsghash.cpp

clean:
	rm -f bitmsghash.o bitmsghash.so bitmsghash*.dll
