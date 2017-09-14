**This repository is in alpha development.**
**forked from** [Py4A on GoogleCode](https://code.google.com/p/python-for-android/)

Download
===
see [Releases page](../../releases), and select an installer:
[PythonForAndroid-debug.apk](https://github.com/kuri65536/python-for-android/releases/download/r26/PythonForAndroid-debug-r26.apk)
.

Status
===
- Python2.7.12
- Python3.6.0

Description
===
This is Python built to run on Android devices.
It is made to be used together with SL4A (Scripting Layer For Android).

Nearly all the actual non-python specific
documentation can be found at [android-scripting](http://code.google.com/p/android-scripting/)

For Python specific issues and enhancements _only_,
please use the issues tab.


Instruction for installation
===
## Normal install
### Requirements
* python2: an Android Device 1.6 >=
* python3: an Android Device 2.3.1 >=
* internet access
* [SL4A](http://github.com/kuri65536/sl4a) was installed.

### How to install
1. Download [SL4A Application](https://github.com/kuri65536/sl4a), such as
   [sl4a-r6.1.1-arm-debug.apk](https://github.com/kuri65536/sl4a/releases/download/6.2.0/sl4a-r6.2.0-arm-debug.apk)
2. Download [Py4A Application](../../releases), such as
   [PythonForAndroid-debug.apk](../../releases/download/r26/PythonForAndroid-debug-r26.apk)
3. Enable "Unknown Sources" in your device settings.
4. Open 1. apk to install. (sl4a)
5. Open 2. apk to install. (py4a)
6. Open PythonForAndroid application
7. Click Install to download and install python binaries.
8. Launch sl4a, Select 'Menu' >> 'View' >> 'Interpreters'
   and Select 'Python 2.7.?'.
9. Python will be launched, have fun!

## Local install

* if you device is not connected to internet, please try this way.

### How to install
1. Download sl4a apk
2. Download py4a apk
3. Download py4a zips, [interpreter - python_r29.zip](../../releases/download/r29/python_r29.zip),
   [modules - python_extras_r29.zip](../../releases/download/r29/python_extras_r29.zip),
   [sample scripts - python_scripts_r26.zip](../../releases/download/r26/python_scripts_r26.zip).
4. Enable "Unknown Sources" in your device settings.
5. Open 1. apk to install. (sl4a)
6. Open 2. apk to install. (py4a)
7. Open PythonForAndroid application
8. push 3. zips to device's /sdcard/com.googlecode.pythonforandroid.
   (be sure /sdcard path to fit your device.)
9. Click "Local install" to check zips and install python binaries.
9. Click "Local install" to install these zips.
10. Launch sl4a, Select 'Menu' >> 'View' >> 'Interpreters'
    and Select 'Python 2.7.?'.
11. Python will be launched, have fun!


<a name="create_issue"></a>Please tell me issues
===
* [Create issue(github)](../../issues/new?title=&body=%2a%20What%20device(s)%20are%20you%20experiencing%20the%20problem%20on%3F%0A%20%20%2a%20ex:%20Nexus%20%3F%3F%3F%0A%2a%20What%20OS%20version%20are%20you%20running%20on%20the%20device%3F%0A%20%20%2a%20ex:%20Andriod%20%3F%3F%3F%0A%2a%20What%20version%20of%20the%20product%20are%20you%20using%3F%0A%20%20%2a%20SL4A%20r%3F%3F%3F%3F%0A%20%20%2a%20PythonForAndroid%20r%3F%3F%0A%2a%20What%20steps%20will%20reproduce%20the%20problem%3F%0A%20%201.%20%0A%20%202.%20%0A%20%203.%20%0A%2a%20What%20is%20the%20expected%20output%3F%20What%20do%20you%20see%20instead%3F%0A%20%20%2a%20expected:%20launch%20%3F%3F%3F%0A%20%20%2a%20see:%20stop%20running%0A%2a%20Please%20provide%20any%20additional%20information%20below.%0A)

Current issue form is here::
```markdown
* What device(s) are you experiencing the problem on?
  * ex: Nexus ???
* What OS version are you running on the device?
  * ex: Andriod ???
* What version of the product are you using?
  * SL4A r????
  * PythonForAndroid r??
* What steps will reproduce the problem?
  1. 
  2. 
  3. 
* Provide logcat for detail.
* What is the expected output%3F What do you see instead?
  * expected: launch ???
  * see: stop running
* Please provide any additional information below.
```

Links
===
Pages
---
* [Examples](docs/examples.md) as cookbooks.
* [Modules](docs/modules.md)
* [Creating APKs](docs/building_apks.md)
* [fullscreenwrapper2](docs/fullscreenwrapper2.md)
* [Versions](docs/versions.md)
* [BuildingModules](docs/building_modules.md)
* [BuildingPython](docs/building_python.md)
* [Python3](python3-alpha/README.md)
* [Show all articles](docs/README.md)

External Links
---
* [SL4A as Parent project](https://github.com/kuri65536/sl4a)
* [Py4A Discussion](http://groups.google.com/group/python-for-android)
* [SL4A Discussion](http://groups.google.com/group/android-scripting)

Similar projects
---
Please do not ask any question about below!

* No relatations: [SL4A in google-source](https://android.googlesource.com/platform/external/sl4a)
* No relatations: [Py4A python2.7](https://googlecode.com/p/android-python27)
* No relatations: [QPython](http://qpython.com)
* No relatations: [Kivy](http://kivy.org)


Instruction for build
===
[Instruction for r16 or ealier](docs/building_ant.md)

Requirements for build
---
* In order to build Py4A you first need to build python for Android platform,
  make sure you have all the dependencies needed for building python 2.7 for your
  distro in Ubuntu run: sudo apt-get build-dep python2.7
* Android NDK >= r10e, maybe < r13 (r13 series does not contain GCC)
* Android SDK >= 21.1.2
* Gradle >= 2.0 (included in Android Studio >= 1.0.2)
* Build packages for build python

    - for openssl: `apt install xutils-dev`
    - for 64bit linux: `apt install lib32z1 lib32stdc++6`
    - (?): `apt install aapt`

How to build
---
* Check the dependencies of library (sample of Ubuntu)
```shell
$ sudo apt install libzlib-dev
```

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
python_r29.zip python_extra_r29.zip ... and so on...
```
* Confirm your binary version.
```shell
$ cd python-build
$ cat LATEST_VERSION
r29
$ cat LATEST_VERSION_EXTRA
r29
$ cat LATEST_VERSION_SCRIPTS
r28
```
* Make a release in github and Upload the binaries to it.
  Please be careful to match the release name and
  confirmed binary versions.

### Local install for confirm the build (direct extracting)
* Requirements: root is required.
* Requirements: python already install.
* Requirements: unzip is needed for extract.

How to run:
* after build, move current directory to python2: `cd python-build`
* run scripts
```shell
$ sd=/sdcard adb=~/install/android-sdk-linux/platform-tools/adb \
  sh ../tools/localinstall.sh
```

<!---
 vi: ft=markdown:et:ts=4:nowrap
 -->
