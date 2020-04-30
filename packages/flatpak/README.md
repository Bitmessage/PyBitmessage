# PyBitmessage Linux flatpak instructions
_Some recent Linux distributions don't support QT4 anymore, hence PyBitmessage
won't run with a GUI. However, if you build PyBitmessage as a flatpak, it will
run in a sandbox which provides QT4.__

## Requirements
First make sure you have `flatpak` and `flatpak-builder` installed. Follow the
instructions for your distribution on [flathub](https://flatpak.org/setup/). The
instructions there only cover the installation of `flatpak`, but 
`flatpak-builder` should be the same.

## Build and Install
Once you have `flatpak` and `flatpak-builder` installed:
```
git clone git://github.com/Bitmessage/PyBitmessage.git
cd PyBitmessage/
git submodule update --init --recursive
flatpak-builder --install --user -install-deps-from=flathub --force-clean --state-dir=build/.flatpak-builder build/_flatpak org.bitmessage.PyBitmessage.json
```
This will install PyBitmessage to your local flatpak user repository, but it 
takes a while to compile because QT4 and PyQt4 have to be build, among others.

# Run
When installation is done you can launch PyBitmessage via the **command line**:
`flatpak run -v org.bitmessage.PyBitmessage`

Flatpak also exports a `.desktop` file, so you should be able to find and launch
PyBitmessage via the **application launcher** of your Desktop (Gnome, KDE, ...).

# Export
You can create a single file "bundle", which allows you to copy and install the
PyBitmessage flatpak on other devices of the same architecture as the build machine.

## Create a local flatpak repository
```
flatpak-builder --repo=build/_flatpak_repo --force-clean --state-dir=build/.flatpak-builder build/_flatpak packages/flatpak/org.bitmessage.PyBitmessage.json
```
This will create a local flatpak repository in `build/_flatpak_repo/`.

## Create a bundle
```
flatpak build-bundle build/_flatpak_repo build/pybitmessage.flatpak org.bitmessage.PyBitmessage
```
This will create a `pybitmessage.flatpak` bundle file in the `build/` directory. 

This bundle can be copied to other systems or installed locally:
```
flatpak install pybitmessage.flatpak
```

The application can be run using flatpak:
```
flatpak run org.bitmessage.PyBitmessage
```

It can then be uninstalled with this command:
```
flatpak uninstall org.bitmessage.PyBitmessage
```

This way of building an application is very convenient when preparing flatpaks
for testing on another system of the same processor architecture.

## Cleanup
If you want to free up disk space you can remove the `Sdk` runtime again:
`flatpak uninstall org.freedesktop.Sdk//18.08`

You can also delete the `build` directory again.
