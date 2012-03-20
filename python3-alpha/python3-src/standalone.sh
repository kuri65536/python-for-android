export EXTERNAL_STORAGE=/mnt/sdcard/com.googlecode.python3forandroid
export PY34A=/data/data/com.googlecode.python3forandroid/files/python3
PYTHONPATH=$EXTERNAL_STORAGE/extras/python3
PYTHONPATH=${PYTHONPATH}:$PY34A/lib/python3.2/lib-dynload
export PYTHONPATH
export TEMP=$EXTERNAL_STORAGE/python3/tmp
export PYTHON_EGG_CACHE=$TEMP
export PYTHONHOME=$PY34A
export LD_LIBRARY_PATH=$PY34A/lib
$PYTHONHOME/bin/python3 "$@"
