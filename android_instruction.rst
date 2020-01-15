PyBitmessage(Android)

This sample aims to be as close to a real world example of a mobile. It has a more refined design and also provides a practical example of how a mobile app would interact and communicate with its addresses.

Steps for trying out this sample:

Compile and install the mobile app onto your mobile device or emulator.


Getting Started

This sample uses the kivy as Kivy is an open source, cross-platform Python framework for the development of applications that make use of innovative, multi-touch user interfaces. The aim is to allow for quick and easy interaction design and rapid prototyping whilst making your code reusable and deployable.

Kivy is written in Python and Cython, supports various input devices and has an extensive widget library. With the same codebase, you can target Windows, OS X, Linux, Android and iOS. All Kivy widgets are built with multitouch support. 

Kivy in support take Buildozer which is a tool that automates the entire build process. It downloads and sets up all the prerequisite for python-for-android, including the android SDK and NDK, then builds an apk that can be automatically pushed to the device.

Buildozer currently works only in Linux, and is an alpha release, but it already works well and can significantly simplify the apk build.

To build this project, use the "Buildozer android release deploy run" command or use.
Buildozer ue=sed for creating application packages easily.The goal is to have one "buildozer.spec" file in your app directory, describing your application requirements and settings such as title, icon, included modules etc. Buildozer will use that spec to create a package for Android, iOS, Windows, OSX and/or Linux.

Installing Requirements

You can create a package for android using the python-for-android project as with using the Buildozer tool to automate the entire process. You can also see Packaging your application for the Kivy Launcher to run kivy programs without compiling them.

You can get buildozer at https://github.com/kivy/buildozer or you can directly install using pip install buildozer

This will install buildozer in your system. Afterwards, navigate to your project directory and run:

buildozer init

This creates a buildozer.spec file controlling your build configuration. You should edit it appropriately with your app name etc. You can set variables to control most or all of the parameters passed to python-for-android.

Install buildozer’s dependencies.

Finally, plug in your android device and run:

buildozer android debug deploy run >> To build, push and automatically run the apk on your device. Here we used debug as tested in debug mode for now.

Packaging your application for the Kivy Launcher


