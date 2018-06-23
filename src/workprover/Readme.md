Please keep this module independent from the outside code, so that it can be reused in other applications.

If you are going to use it, you should wrap your program's main file in this:

```python
import workprover.dumbsolver

workprover.dumbsolver.libcrypto = ...

if __name__ == "__main__":
    import multiprocessing

    multiprocessing.freeze_support()

    ...
```

See the `multiprocessing` module documentation for explaination.

Build fast solver
-----------------

On Linux, BSDs or MacOS: `make -C fastsolver`.

On Windows:

- Install OpenSSL. Build it yourself or install [third-party](https://wiki.openssl.org/index.php/Binaries) prebuilt binaries.

- Install MSVC as part of Visual Studio or standalone. Official offline installer: https://aka.ms/vcpython27.

- Open its command line and go to the `fastsolver` directory.

- Add OpenSSL paths to environment variables:

```bat
set INCLUDE=C:\OpenSSL-Win64\include;%INCLUDE%
set LIB=C:\OpenSSL-Win64\lib;%LIB%
```

- Do `cl @options.txt`.

- Append the `-32` or `-64` suffix to the DLL file name.
