#! /bin/sh
st=`for i in /mnt/storage /mnt/sdcard /sdcard; do [ -d $i ] && echo $i && break; done`

PW=`pwd`
export EXTERNAL_STORAGE=$st
export LANG=en
PYTHONPATH=$st/com.googlecode.pythonforandroid/extras/python
PYTHONPATH=${PYTHONPATH}:/data/data/com.googlecode.pythonforandroid/files/python/lib/python2.7/lib-dynload
export PYTHONPATH
export TEMP=$st/com.googlecode.pythonforandroid/extras/python/tmp
export PYTHON_EGG_CACHE=$TEMP
export PYTHONHOME=/data/data/com.googlecode.pythonforandroid/files/python
export LD_LIBRARY_PATH=/data/data/com.googlecode.pythonforandroid/files/python/lib
cd $PW
/data/data/com.googlecode.pythonforandroid/files/python/bin/python $*

