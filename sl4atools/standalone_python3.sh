#! /bin/sh
st=`for i in /mnt/storage /mnt/sdcard /sdcard; do [ -d $i ] && echo $i && break; done`

PW=`pwd`
export EXTERNAL_STORAGE=$st
export LANG=en
bin=/data/data/com.googlecode.python3forandroid/files/python3
ext=$st/com.googlecode.python3forandroid/extras/python3
PYTHONPATH=$ext
PYTHONPATH=${PYTHONPATH}:$bin/lib/python3.4/lib-dynload
export PYTHONPATH
export TEMP=$ext/tmp
export PYTHON_EGG_CACHE=$TEMP
# do not use this for Python3... see issue tracker.
# export PYTHONHOME=$bin
export LD_LIBRARY_PATH=$bin/lib
cd $PW
$bin/bin/python3 "$@"

