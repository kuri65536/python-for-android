* [Report issue](../README.md#create_issue)

Running Python from a shell
===
The necessary environment settings required to run python from a shell script can be found here:

* for Python2: [../sl4atools/python2.sh](../sl4atools/python2.sh)
* for Python3: [../sl4atools/python3.sh](../sl4atools/python3.sh)

To use, make the script executable and run from the shell:

```shell
chmod a+x python2.sh
./python2.sh
```

or, if that doesn't work (and it may not, depending on filesystem) just:

`sh /sdcard/python2.sh`

The script at time of writing looks like this:

```shell
#! /bin/sh

export EXTERNAL_STORAGE=/mnt/storage
PYTHONPATH=/mnt/storage/com.googlecode.pythonforandroid/extras/python
PYTHONPATH=${PYTHONPATH}:/data/data/com.googlecode.pythonforandroid/files/python/lib/python2.6/lib-dynload
export PYTHONPATH
export TEMP=/mnt/storage/com.googlecode.pythonforandroid/extras/python/tmp
export PYTHON_EGG_CACHE=$TEMP
export PYTHONHOME=/data/data/com.googlecode.pythonforandroid/files/python
export LD_LIBRARY_PATH=/data/data/com.googlecode.pythonforandroid/files/python/lib
/data/data/com.googlecode.pythonforandroid/files/python/bin/python "$@"
```

Note that you can pass arguments to python, ie:

`./python2.sh hello.Py`

Why is it so complicated?
---
Android is quite fussy about what it lets you have access to. Executables and shared libraries
have to be on the main file system (typically /data/data somewhere)

The only writable parts of /data/data are the ones allocated to your package (apk) (ie:
/data/data/com.googlecode.pythonforandroid ) although you can use chmod to override this.

Bulky items should live on the /sdcard, (not always an actual sdcard). Android allocates a package
based spot to store this stuff (ie, /sdcard/com.googlecode.pythongorandroid/extras). For most
android devices, space in the main fs is at a premium. Thus the extensive library files are places
on the /sdcard.

Python needs to be told where all these non-standard places are. (Thus, PYTHONHOME etc)

<!---
 vi: ft=markdown:et:ts=4:fdm=marker
 -->
