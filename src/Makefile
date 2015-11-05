all:
	@echo "This compiles and tests the C PoW library, it's not necessary to run PyBitmessage"

powtest:
	./testpow.py

bitmsghash.so: bitmsghash.o
	g++ bitmsghash.o -shared -fPIC -lpthread -lcrypto -o bitmsghash.so

bitmsghash.o:
	g++ -Wall -O3 -march=native -fPIC -c bitmsghash.cpp

clean:
	rm -f bitmsghash.o bitmsghash.so

