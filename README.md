This repository is alpha development. forked from [GoogleCode](https://code.google.com/p/python-for-android/)
===

Instruction for installation
===
Requirements
---
* an Android Device 1.6 >=
* [SL4A](http://github.com/kuri65536/sl4a) was installed.

How to install
---
1. Download [SL4A Application](https://github.com/kuri65536/sl4a), such as
   [sl4a-r6x04-arm-debug.apk](https://github.com/kuri65536/sl4a/releases/download/6x04/sl4a-r6x04-arm-debug.apk)
2. Downlaod [Py4A Application](https://github.com/kuri65536/python-for-android/releases), such as
   [PythonForAndroid-debug.apk](https://github.com/kuri65536/python-for-android/releases/download/r17/PythonForAndroid-debug.apk)
3. Enable "Unknown Sources" in your device settings.
4. Open 1. apk to install.
5. Open 2. apk to install.
6. Open PythonForAndroid application
7. Click Install to download and install python binaries.


Links
===
Pages
---
* [BuildingModules](docs/building_modules.md)
* [BuildingPython](docs/building_python.md)
* [Modules](docs/modules.md)
* [Python3](python3-alpha/README.md)
* [Versions](docs/versions.md)
* [fullscreenwrapper2]()
* [Show all](docs/README.md)

External Links
---
* [SL4A as Parent project](https://github.com/kuri65536/sl4a)
* [Py4A Discussion](http://groups.google.com/group/python-for-android)
* [SL4A Discussion](http://groups.google.com/group/android-scripting)


Instruction for build
===

Requirements for build
---
* In order to build Py4A you first need to build python for Android platform,
  make sure you have all the dependencies needed for building python 2.7 for your
  distro in Ubuntu run: sudo apt-get build-dep python2.7
* Android NDK >= r10d
* Android SDK >= 21.1.2

How to build
---
* Clone this project.
```shell
for Mercurial uesr (with hg-git plugin)
$ hg clone git://github.com/kuri65536/python-for-android

for git user
$ git clone git://github.com/kuri65536/python-for-android
```
* Build the apk:
```shell
$ cd android/PythonForAndroid
$ echo sdk.dir=/path/to/android-sdk > local.properties
$ sh /path/to/android-stdudio/gradle/gradle-2.2.1/bin/gradle assembleDebug
Building ??% ...
$ ls build/outputs/apk/
PythonForAndroid-debug.apk
```
* Build the py4a binaries.
```shell
$ cd python-build
$ NDK_PATH=/path/to/android-ndk-r10d make build
$ ls python*.zip
python_r18.zip python_extra_r18.zip ... and so on...
```
* Confirm your binary version.
```shell
$ cd python-build
$ cat LATEST_VERSION
r17
$ cat LATEST_VERSION_EXTRA
r17
$ cat LATEST_VERSION_SCRIPTS
r17
```
* Make a release in github and Upload the binaries to it.
  Please be careful to match the release name and
  confirmed binary versions.
* Install sl4a to your device.
* Install py4a to your device.
* Launch sl4a, Select 'Menu' >> 'View' >> 'Interpreters'
  and Select 'Python 2.7.?'.
* Python will be launched, have fun!


Old instruction (use ant)
===
* In Ubuntu (i386) you need to run this before anything else:
```shell
export LDFLAGS="-L /usr/lib/i386-linux-gnu/"

pushd python-build
bash build.sh
popd
```
* Then you need to update the references for the APK file
```shell
pushd python-build
python update-apk.py
popd
```
* Next step is building a few Android libraries needed for Py4A to be built.
```shell
pushd android
pushd Utils
ant
popd
pushd Common
ant
popd
pushd InterpreterForAndroid
ant
popd
popd
```
* Now build Py4A apk signing with debug key
```shell
pushd android/PythonForAndroid
mkdir libs
cp ../{Utils,Common,InterpreterForAndroid}/dist/*.jar libs
ant debug
popd
```

<!---
 vi: ft=markdown:et:ts=4:nowrap
 -->
