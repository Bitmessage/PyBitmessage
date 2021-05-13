#!/bin/sh

#####################################################################
# Usage:  ./build.sh "path to deb package"
# Example  ./build.sh ~/Downloads/pybitmessage_0.6.3.2-1_amd64.deb 
#####################################################################

#CleanUp Old Builds 
rm -rf AppDir/
rm -rf tmp/

mkdir AppDir
mkdir tmp

echo 'Building from inputFile:' $1 

dpkg -x $1 tmp/

mv tmp/usr/ AppDir/usr/
cp AppRun AppDir/
cp AppDir/usr/share/applications/pybitmessage.desktop AppDir/
cp AppDir/usr/share/icons/hicolor/24x24/apps/pybitmessage.png AppDir/
ARCH=x86_64 appimagetool AppDir/

##Clean-up
rm -rf AppDir/
rm -rf tmp/

echo "Build Successful"
echo "Run ./PyBitmessage-x86_64.AppImage"