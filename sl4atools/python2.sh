#! /system/bin/sh
st=`for i in /mnt/storage /mnt/sdcard /sdcard; do [ -d $i ] && echo $i && break; done`
if [ x$api != x ]; then :
elif ! type \cut > /dev/null; then api=14; else
    api=`grep build.version.sdk /system/build.prop | cut -d = -f 2`
fi

# android.Android() will launch SL4A server, if server down.

PW=`pwd`
ver=2.7
py4a=pythonforandroid
binr=python
export EXTERNAL_STORAGE=$st
export LANG=en
bin=/data/data/com.googlecode.$py4a/files/$binr
pfx=$st/com.googlecode.$py4a
ext=$pfx/extras/$binr
PYTHONUSERBASE=$pfx/local
PYTHONPATH=$ext
PYTHONPATH=${PYTHONPATH}:$PYTHONUSERBASE
PYTHONPATH=${PYTHONPATH}:$bin/lib/python$ver/lib-dynload
export PYTHONPATH
export PYTHONUSERBASE
export TEMP=$ext/tmp
export PYTHON_EGG_CACHE=$TEMP
export PYTHONHOME=/data/data/com.googlecode.pythonforandroid/files/python
export LD_LIBRARY_PATH=$bin/lib
cd $PW
if [ $api -lt 14 ]; then
    run=/data/data/com.googlecode.android_scripting/files/run_pie
    if ! [ -x $run ]; then
        echo "need root permission to launch run_pie/python"
        ls -l "$run"
        # su -c "chmod 755 $run"    # this was failed...
        su -c "$run $bin/bin/python $*"
    else
        $run $bin/bin/python $*
    fi
else
    $bin/bin/python $*
fi

