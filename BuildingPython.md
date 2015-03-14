# Introduction #
How to build Python for Android.


# Details #
_For linux_

Download and install [Android NDK](http://developer.android.com/sdk/ndk/index.html).

Grab the latest [Py4A Source](http://code.google.com/p/python-for-android/source/checkout).

The build script needs to be able to find both _ndk-build_ and _arm-eabi-strip_. Here is an example of how to set your path:

```
export ANDROID_NDK=~/android-ndk-r5
export PATH=$PATH:$ANDROID_NDK:$ANDROID_NDK/toolchains/arm-eabi-4.4.0/prebuilt/linux-x86
```

Then, to actually build python:

```
bash build.sh
```

See: BuildingModules for how to build modules.