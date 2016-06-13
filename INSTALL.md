# PyBitmessage Installation Instructions 

For an up-to-date version of these instructions, please visit the
[Bitmessage Wiki](https://bitmessage.org/wiki/Compiling_instructions).

PyBitmessage can be run either straight from source or as an installed
package.

## Dependencies
Before running PyBitmessage, make sure you have all the necessary dependencies
installed on your system.

Dependencies needed for PyBitmessage:
- Python 2.7 (`python2.7`)
- PyQT 4 (`python-qt4`)
- OpenSSL (`openssl`)

Additionally for Fedora and Redhat distros:
- `openssl-compat-bitcoin-libs`

## Running PyBitmessage
PyBitmessage can be run two ways: straight from source or via a package which
is installed on your system. Since PyBitmessage is beta software, it is best
to run PyBitmessage from source as you can update as needed.

#### Updating
To update PyBitmessage from source (Linux/OS X), you can do these easy steps:
```shell
cd PyBitmessage/src/
git fetch --all
git reset --hard origin/master
python bitmessagemain.py
```
Voilà! Bitmessage has been updated!

#### Linux
To run PyBitmessage from the command line, you must download the source, then
run `src/bitmessagemain.py`.
```shell
git clone https://github.com/Bitmessage/PyBitmessage.git
cd PyBitmessage/ && python src/bitmessagemain.py
```

That's it! *Honestly*!

#### Windows
On Windows you can download the lastest executable for Bitmessage
[here](https://bitmessage.org/download/windows/Bitmessage.exe).

However, if you would like to run PyBitmessage via Python in Windows, you can
go [here](https://bitmessage.org/wiki/Compiling_instructions#Windows) for more
information on how to do so.

#### OS X
First off, install Homebrew.
```shell
ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"
```

Now, install the required dependencies:
```shell
brew install git python pyqt
```

Download and run PyBitmessage:
```shell
git clone git://github.com/Bitmessage/PyBitmessage.git
cd PyBitmessage && python src/bitmessagemain.py
```

## Creating a package for installation
If you really want, you can make a package for PyBitmessage, which you may
install yourself or distribute to friends. This isn't recommended, since
PyBitmessage is beta software and subject to frequent change.

#### Linux

First off, since PyBitmessage uses something nifty called
[packagemonkey](https://github.com/fuzzgun/packagemonkey), go ahead and get
that installed. You may have to build it from source.

Next, edit the `generate.sh` script to your liking.

Now, run the appropriate script for the type of package you'd like to make:

- `arch.sh` - create a package for Arch Linux
- `debian.sh` - create a package for Debian/Ubuntu
- `ebuild.sh` - create a package for Gentoo
- `osx.sh` - create a package for OS X
- `puppy.sh` - create a package for Puppy Linux
- `rpm.sh` - create a RPM package
- `slack.sh` - create a package for Slackware

#### OS X
Please refer to
[this page](https://bitmessage.org/forum/index.php/topic,2761.0.html) on the
forums for instructions on how to create a package on OS X.

Please note that some versions of OS X don't work.

#### Windows
##### TODO: Create Windows package creation instructions
