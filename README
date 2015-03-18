This repository is alpha development. forked from [GoogleCode](https://code.google.com/p/python-for-android/)
===

Requirements
===

* In order to build Py4A you first need to build python for Android platform,
  make sure you have all the dependencies needed for building python 2.7 for your
  distro in Ubuntu run: sudo apt-get build-dep python2.7

* Android NDK
* Android SDK


Instruction
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
