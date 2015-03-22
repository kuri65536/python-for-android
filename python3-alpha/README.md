Introduction
===
This page is about the Python3 port to Android
Details

I have started a conversion of Python3 for Android, tentatively codenamed Py3k4a.

A Beta release of Python3.2.2 for Android is available here:

http://code.google.com/p/python-for-android/downloads/detail?name=Python3ForAndroid_r6.apk
Instructions

To use:

    You must have Android 2.3.1 or later. Earlier versions do not have even rudimentary wide
character support, which Python3 uses extensively.
    Completely uninstall Py4a (Python 2.6.2) both with the Uninstall button in the Py4a app, and
Settings-->Applications-->Manage Applications-->Python for Android-->Uninstall
    Install the Python3ForAndroid apk
    Open the Python3 for Android application, and hit the "Install" button. (It may say
"Uninstall" when you first go in. Hit that button and it will quickly change to "Install".)
    You'll need web access to download the Python3 runtime environment. This may take a little
while.
    As part of the download, it may ask to overwrite the sample scripts. Say "Yes to All", as the
sample python2 scripts have been converted in Python3 syntax. 

Python Code Updates

As of Python3ForAndroid_r5.apk, new versions of the Python binaries can installed as they become
available. Check the Installed vs Available versions (displayed in the Installer screen). In the
available is later than the installed, simply uninstall then reinstall. No need to re-install the
apk.
State of Play

As of 19-Apr-2012

Python3 exists in an Beta release. All the basic modules that android can support have been
included.

All of the usual additional modules have been added (although new versions as might be expected)

I have got sqlite3 importing, and also hashlib and ssl working with the latest openssl libraries.

readline is now implemented, allowing command line editing from within the interpreter.

curses is implemented, allowing text-based screen control.

bzip2 and ctypes are now included.

The Python3 build module is in the python-for-android repository under 'python3-alpha'. This may
have bloated the repository notably... oops.

Build instructions:

    Install android toolchain
    Make sure the toolchain bin folder is in your path.
    from python3-alpha, run 'buildall.sh' 

Things not working:

    egg handling (the install modules stuff is potentially working but untested) 

Next steps:

    Get the modules installation working for Python3. first pass done
    Work out eggifying process for Python3 impure modules
    Tidy up installation process. (At the moment, it's all loaded from 

the website. I'll look at embedded and manual install options)

    Go through the currently installed modules, trim if needed, convert 

to pyc for speed. (NB: this is what we do with Py4a at present... is it actually still desirable?)

What I need:

    General testing and feedback. Let me know what doesn't work, and what extra bits are
desirable. 

Running from the command line

This script will allow you to run Python3 from the command line: Standalone Script

I usually test by going:

adb push standalone.sh /sdcard/standalone.sh
adb shell
sh /sdcard/standalone.sh

Note that the script takes arguments.

The reason to put in on /sdcard is that should be writable on almost any device.
Importing Modules

As of apk r6 and version 9 of the install files, there is support for importing (pure python)
modules using pip and distribute This is still a little messy, but seems to basically work.

How to use:

    Use latest python3forandroid_r6.apk
    Install latest python versions (9,9,9)
    Run 'distribute_setup.py' (included in scripts) (NB: This can take a while, and may pause on
''skipping ws_comma' for quite a long time)
    Download https://raw.github.com/pypa/pip/master/contrib/get-pip.py into /sdcard/sl4a/scripts,
and run it. 

Once installed, you can install packages from pypi etc as follows:

import pip
pip.main(['install','pytz'])

(pytz is used as an example)

Since pip is intended to be run from the command line, I've included at utility called
'pip_console.py' which will emulate this behavior.

I've added some notes on Cross Compiling Python 

android_notes.txt
---
* In pyconfig.h, #undef set_locale // ignore

* manually set group and seperator in localeutil.h (and other locale operations)
* remove any references to localconv()
* set up ANDROID 1 in pyconfig.h for code changes.
* remove localconv() refs in _localmodule.c (#define ANDROID) to return NULL.
* change setup.py (in detect modules) to be able to find cross-compiled builds. Also remove refs to /usr/local etc in crosscompile mode.
* build replacement mbstowcs and wcstombs as these DON'T WORK AT ALL in android, and in fact seem to screw up memory.
* change site.py to not fall over when trying to parse makefile.
