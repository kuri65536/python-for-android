# Introduction #

A guide on how to build Python Modules.
_Note: For 2.6.2 Python. 3.2.2 is still in development_

# Setup #

Download the latest python-lib from our [Downloads](Downloads.md) section, _At time of writing, this is:_
```
python-lib_r14.zip
```

Unzip this into python-modules/python-lib


# Using setuptools - Creating Egg #
## NDK setup ##
In order to build binary modules you need to have Android NDK installed and correctly setup. Download the latest NDK, drop it somewhere, do a [toolchain installation](Toolchain_Installation.md), and then export the next variables:
```
export ANDROID_NDK_TOOLCHAIN_ROOT=<path to installed toolchain>
```

## Setup setup.py ##
In order to use setuptools with Android a few changes need to be done into your setup.py script. First you need to monkey patch setuptools, we provide with a helper script for this, edit your setup.py and add this lines **before** calling **setup**
```
from py4a import patch_distutils
patch_distutils()
```

You also need to either pass **-p linux-armv** or create a file **setup.cfg** inside the same folder than setup.py with this content
```
[bdist_egg]
plat-name=linux-armv
```

## Setup environment ##
If your project uses binary modules, the build process is a bit rougher, but still a lot of fun. Before calling build you need to import a shell script that will setup your environment to work, this script is called **setup.sh** and is part of the python-lib package.

So supposing we're working on projectX, and our folder structure is this:
```
python-lib
..........setup.sh
projectX
..........setup.py
..........setup.cfg
```

Then you would do from projectX.
```
source ../python-lib/setup.sh
```

## Cooking your eggs ##
Ok so it's time to cook an egg. Once we have all the setup done it's time to boil the water and cook an egg.

If everything is fine the process is simple just do the regular ` python setup.py bdist_egg `. If it doesn't work for you, then start looking at our other modules, and start asking questions in our mailing list, we don't bite.


## Stuff below this line is more or less obsolete ##
But may still be useful...

# Non egg projects #
cd to the folder containing your module, and run:
```
bash build.sh
```

There are now several modules built and supported by !Py4a. See [Modules](Modules.md).

## How to Build your Own Modules ##
Currently, the best advice is to look at how pybluez was built, in python-modules/pybluez.

At this time, we are working on a more comprehensive guide.

### Rough Guide ###
If your module is pure python, then using it is as simple as copying the module into your phone. The best path for this is:
/sdcard/com.googlecode.pythonforandroid/extras/python

If it contains C or C++ source code, it gets more complex. Currently we are using the Android NDK to manage module builds. This is easy to install, but requires a little setup to make it compile the needed .so files.

In general, you need to:
  * Copy the .c and .h files into a jni folder.
  * Set up an android.mk to tell ndk-build what to do.
  * set up a script to run ndk-build and then copy the needed python and .so files into a zip.

See the source for pybluez for a simple example, and for twisted for something more complex.

Documentation on the Android.mk can be found in the android-ndk docs folder.