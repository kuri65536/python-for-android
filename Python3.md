# Introduction #

This page is about the Python3 port to Android


# Details #

I have started a conversion of Python3 for Android, tentatively codenamed Py3k4a.

A Beta release of Python3.2.2 for Android is available here:

http://code.google.com/p/python-for-android/downloads/detail?name=Python3ForAndroid_r6.apk

## Instructions ##

To use:
  * You must have Android 2.3.1 or later. Earlier versions do not have even rudimentary wide character support, which Python3 uses extensively.
  * Completely uninstall Py4a (Python 2.6.2) both with the Uninstall button in the Py4a app, and Settings-->Applications-->Manage Applications-->Python for Android-->Uninstall
  * Install the Python3ForAndroid apk
  * Open the Python3 for Android application, and hit the "Install" button. (It may say "Uninstall" when you first go in. Hit that button and it will quickly change to "Install".)
  * You'll need web access to download the Python3 runtime environment. This may take a little while.
  * As part of the download, it may ask to overwrite the sample scripts. Say "Yes to All", as the sample python2 scripts have been converted in Python3 syntax.

#### Python Code Updates ####
As of Python3ForAndroid\_r5.apk, new versions of the Python binaries can
installed as they become available.
Check the Installed vs Available versions (displayed in the Installer screen). In the available is later than the installed, simply uninstall then reinstall. No need to re-install the apk.

## State of Play ##
_As of 19-Apr-2012_

Python3 exists in an Beta release. All the basic modules that android can support have been included.

All of the usual additional modules have been added (although new versions as might be expected)

I have got sqlite3 importing, and also hashlib and ssl working with
the latest openssl libraries.

readline is now implemented, allowing command line editing from within the interpreter.

curses is implemented, allowing text-based screen control.

bzip2 and ctypes are now included.

The Python3 build module is in the python-for-android repository under 'python3-alpha'. This may have bloated the repository notably... oops.

Build instructions:
  * Install [android toolchain](Toolchain_Installation.md)
  * Make sure the toolchain bin folder is in your path.
  * from python3-alpha, run 'buildall.sh'

### Things not working: ###
  * egg handling (the install modules stuff is potentially working but untested)

### Next steps: ###

  * Get the modules installation working for Python3. _first pass done_
  * Work out eggifying process for Python3 impure modules
  * Tidy up installation process. (At the moment, it's all loaded from
the website. I'll look at embedded and manual install options)
  * Go through the currently installed modules, trim if needed, convert
to pyc for speed. (NB: this is what we do with Py4a at present... is
it actually still desirable?)

### What I need: ###
  * General testing and feedback. Let me know what doesn't work, and what extra bits are desirable.

## Running from the command line ##
This script will allow you to run Python3 from the command line:
[Standalone Script](http://code.google.com/p/python-for-android/source/browse/python3-alpha/python3-src/standalone.sh)

I usually test by going:
```
adb push standalone.sh /sdcard/standalone.sh
adb shell
sh /sdcard/standalone.sh
```

Note that the script takes arguments.

The reason to put in on /sdcard is that should be writable on almost any device.

## Importing Modules ##
As of apk [r6](https://code.google.com/p/python-for-android/source/detail?r=6) and version 9 of the install files, there is support for importing (pure python) modules using **pip** and **distribute**
This is still a little messy, but seems to basically work.

How to use:
  * Use latest python3forandroid\_r6.apk
  * Install latest python versions (9,9,9)
  * Run 'distribute\_setup.py' (included in scripts) (NB: This can take a while, and may pause on ''skipping ws\_comma' for quite a long time)
  * Download https://raw.github.com/pypa/pip/master/contrib/get-pip.py into /sdcard/sl4a/scripts, and run it.

Once installed, you can install packages from pypi etc as follows:
```
import pip
pip.main(['install','pytz'])
```

(pytz is used as an example)

Since pip is intended to be run from the command line, I've included at utility called 'pip\_console.py' which will emulate this behavior.

I've added some notes on [Cross Compiling Python](CrossCompilingPython.md)