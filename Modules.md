# Introduction #

List of pre-built python modules.

## PySerial ##
This module encapsulates the access for the serial port

Home Page: http://pyserial.sourceforge.net/

Download: [pyserial-2.6-py2.6.egg](http://python-for-android.googlecode.com/files/pyserial-2.6-py2.6.egg)

Egg contributed by Robin Gilham

## PyBluez ##
A library for Bluetooth functionality.

Home page: http://code.google.com/p/pybluez/

Download: [PyBluez-0.19-py2.6-linux-armv.egg](http://python-for-android.googlecode.com/files/PyBluez-0.19-py2.6-linux-armv.egg)

## Twisted ##
An event-driven networking engine written in Python.

Home page: http://twistedmatrix.com/trac/

Download: [Twisted-12.0.0-py2.7-linux-armv.egg](http://python-for-android.googlecode.com/files/Twisted-12.0.0-py2.7-linux-armv.egg)

Required Zope interface (see below)

## Zope ##
An interface to zope.

Home page: http://www.zope.org/Products/ZopeInterface

Download: [zope.interface-3.3.0-py2.7-linux-armv.egg](http://python-for-android.googlecode.com/files/zope.interface-3.3.0-py2.7-linux-armv.egg)

Required by twisted.

## pyEphem ##
PyEphem provides scientific-grade astronomical computations

Home Page: http://rhodesmill.org/pyephem/

Download: http://python-for-android.googlecode.com/files/pyephem-3.7.4.1-py2.6-linux-armv.egg

## pyCrypto ##
The Python Cryptography Toolkit

Home page: https://www.dlitz.net/software/pycrypto/

[pycrypto-2.3-py2.7-linux-armv.egg](http://python-for-android.googlecode.com/files/pycrypto-2.3-py2.7-linux-armv.egg)

There may be others we forgot to update.
Look here for more: [Module Downloads](http://code.google.com/p/python-for-android/downloads/list?q=Type-Module)

# Requests we can't do yet #
Anything requiring Qt, Tk, or SDL is right out at present, because Android really doesn't support them. This includes PySide, PyQt, PyGtk and PyGames. And wxPython.

Yes, there are ports in progress, but the important point is that sl4a (which py4a runs under) doesn't offer a mechanism to support these features.

This is not to say they will **never** be supplied, but not in the short term, and each technology is significant sub-project in its own right.

# How can I contribute my own Modules? #
Send link to the mailing list, and if it looks OK we'll add it.