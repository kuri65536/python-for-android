#! /bin/sh
st=`for i in /mnt/storage /mnt/sdcard /sdcard; do [ -d $i ] && echo $i && break; done`
if [ x$api != x ]; then :
elif ! type \cut > /dev/null; then api=14; else
    api=`grep build.version.sdk /system/build.prop | cut -d = -f 2`
fi


PW=`pwd`
export EXTERNAL_STORAGE=$st
export LANG=en
bin=/data/data/com.googlecode.pythonforandroid/files/python
ext=$st/com.googlecode.pythonforandroid/extras/python
PYTHONPATH=$ext
PYTHONPATH=${PYTHONPATH}:$bin/lib/python2.7/lib-dynload
export PYTHONPATH
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

