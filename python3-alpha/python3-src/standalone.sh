export EXTERNAL_STORAGE=/mnt/sdcard/com.googlecode.python3forandroid
export PY34A=/data/data/com.googlecode.python3forandroid/files/python3
export PY4A_EXTRAS=$EXTERNAL_STORAGE/extras
PYTHONPATH=$EXTERNAL_STORAGE/extras/python3
PYTHONPATH=${PYTHONPATH}:$PY34A/lib/python3.2/lib-dynload
export PYTHONPATH
export TEMP=$EXTERNAL_STORAGE/extras/python3/tmp
export HOME=/sdcard
export PYTHON_EGG_CACHE=$TEMP
export PYTHONHOME=$PY34A
export LD_LIBRARY_PATH=$PY34A/lib
$PYTHONHOME/bin/python3 "$@"
