# PyBitmessage Installation Instructions

For an up-to-date version of these instructions, please visit the
[Bitmessage Wiki](https://bitmessage.org/wiki/Compiling_instructions).

PyBitmessage can be run in either one of two ways:

- straight from source

 or
- from an installed
package.

## Dependencies
Before running PyBitmessage, make sure you have all the necessary dependencies
installed on your system.

Here's a list of dependencies needed for PyBitmessage
- python2.7
- python2-qt4 (python-qt4 on Debian/Ubuntu)
- openssl
- (Fedora & Redhat only) openssl-compat-bitcoin-libs

## Running PyBitmessage
PyBitmessage can be run in two ways:
- straight from source

 or
- via a package which is installed on your system. Since PyBitmessage is Beta, it is best to run
PyBitmessage from source, so that you may update as needed.

#### Updating
To update PyBitmessage from source (Linux/OS X), you can do these easy steps:
```
cd PyBitmessage/src/
git fetch --all
git reset --hard origin/master
python bitmessagemain.py
```
Voilà! Bitmessage is updated!

#### Linux
_Some recent Linux distributions don't support QT4 anymore, hence PyBitmessage
won't run with a GUI. However, if you build PyBitmessage as a flatpak, it will
run in a sandbox which provides QT4. See the **Linux flatpak** instructions 
in the **Creating a package for installation** section of this document._

To run PyBitmessage from the command-line, you must download the source, then
run `src/bitmessagemain.py`.
```
git clone git://github.com/Bitmessage/PyBitmessage.git
cd PyBitmessage/ && python src/bitmessagemain.py
```

That's it! *Honestly*!

#### Windows
On Windows you can download an executable for Bitmessage
[here](https://github.com/Bitmessage/PyBitmessage/releases/download/0.6.3.2/Bitmessage_x86_0.6.3.2.exe).

However, if you would like to run PyBitmessage via Python in Windows, you can
go [here](https://bitmessage.org/wiki/Compiling_instructions#Windows) for
information on how to do so.

#### OS X
First off, install Homebrew.
```
ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"
```

Now, install the required dependencies
```
brew install git python openssl cartr/qt4/pyqt@4 
```

Download and run PyBitmessage:
```
git clone git://github.com/Bitmessage/PyBitmessage.git
cd PyBitmessage && python src/bitmessagemain.py
```

## Creating a package for installation
If you really want, you can make a package for PyBitmessage, which you may
install yourself or distribute to friends. This isn't recommended, since
PyBitmessage is in Beta, and subject to frequent change.

#### Linux
First off, since PyBitmessage uses something nifty called
[packagemonkey](https://github.com/fuzzgun/packagemonkey), go ahead and get
that installed. You may have to build it from source.

Next, edit the generate.sh script to your liking.

Now, run the appropriate script for the type of package you'd like to make
```
arch.sh - create a package for Arch Linux
debian.sh - create a package for Debian/Ubuntu
ebuild.sh - create a package for Gentoo
osx.sh - create a package for OS X
puppy.sh - create a package for Puppy Linux
rpm.sh - create a RPM package
slack.sh - create a package for Slackware
```

#### Linux flatpak
First make sure you have `flatpak` and `flatpak-builder` installed. Follow the
instructions for your distribution on [flathub](https://flatpak.org/setup/). The
instructions there only cover the installation of `flatpak`, but 
`flatpak-builder` should be the same.

Once you have `flatpak` and `flatpak-builder` installed:
```
git clone git://github.com/Bitmessage/PyBitmessage.git
cd PyBitmessage/
git submodule add https://github.com/flathub/shared-modules.git
flatpak-builder --install build/_flatpak -install-deps-from=flathub --force-clean --user org.bitmessage.PyBitmessage.json
```
This will install PyBitmessage to your local flatpak user repository, but it 
takes a while to compile because QT4 and PyQt4 have to be build, among others.

When done you can launch PyBitmessage via:
`flatpak run -v org.bitmessage.PyBitmessage`

If you want to free up disk space you can remove the `Sdk` runtime again:
`flatpak uninstall org.freedesktop.Sdk//18.08`

#### OS X
Please refer to
[this page](https://bitmessage.org/forum/index.php/topic,2761.0.html) on the
forums for instructions on how to create a package on OS X.

Please note that some versions of OS X don't work.

#### Windows
## TODO: Create Windows package creation instructions
