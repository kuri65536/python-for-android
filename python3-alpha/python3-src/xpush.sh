. ../VERSIONS
rm -r android
mkdir android
mkdir android/bin
mkdir android/extras
unzip python3_r${PY34A_VERSION}.zip -dandroid/bin
unzip python3_extras_r${PY34A_EXTRAS_VERSION}.zip -dandroid/extras
cd android
cd bin
adb push python3 /data/data/com.googlecode.python3forandroid/files/python3
cd ../extras
adb push * /sdcard/com.googlecode.python3forandroid/extras/python3
