#! /system/bin/sh
st=`for i in /mnt/storage /mnt/sdcard /sdcard; do [ -d $i ] && echo $i && break; done`
if [ x$api != x ]; then :
elif ! type \cut > /dev/null; then api=14; else
    api=`grep build.version.sdk /system/build.prop | cut -d = -f 2`
fi

# android.Android() will launch SL4A server, if server down.

PW=`pwd`
ver=`python --version | cut -d " "  -f 2 | cut -d . -f 1-2`
export EXTERNAL_STORAGE=$st
export LANG=en
bin=/data/data/com.googlecode.python3forandroid/files/python3
ext=$st/com.googlecode.python3forandroid/extras/python3
PYTHONPATH=$ext
PYTHONPATH=${PYTHONPATH}:$bin/lib/python$ver/lib-dynload
export PYTHONPATH
export TEMP=$ext/tmp
export PYTHON_EGG_CACHE=$TEMP
# do not use this for Python3... see issue tracker.
# export PYTHONHOME=$bin
export LD_LIBRARY_PATH=$bin/lib
cd $PW
if [ $api -lt 14 ]; then
    run=/data/data/com.googlecode.android_scripting/files/run_pie
    if ! [ -x $run ]; then
        echo "need root permission to launch run_pie/python"
        ls -l "$run"
        # su -c "chmod 755 $run"
        su -c "$run $bin/bin/python3 $*"
    else
        $run $bin/bin/python3 $*
    fi
else
    $bin/bin/python3 $*
fi

