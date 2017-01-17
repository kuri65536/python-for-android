#! /system/bin/sh
st=`for i in /mnt/storage /mnt/sdcard /sdcard; do [ -d $i ] && echo $i && break; done`
if [ x$api != x ]; then :
elif ! type \cut > /dev/null; then api=14; else
    api=`grep build.version.sdk /system/build.prop | cut -d = -f 2`
fi

# launch SL4A server is you want.
if false; then
    export AP_PORT='8888' # SL4A Port
    sl4a=com.googlecode.android_scripting
    am start -a $sl4a.action.LAUNCH_SERVER -n
        $sl4a/.activity.ScriptingLayerServiceLauncher --ei
        $sl4a.extra.USE_SERVICE_PORT $AP_PORT
    sleep 2
fi


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

