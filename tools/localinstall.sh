#! /bin/bash
cat <<EOF
* you should have rooted phone.
* you must click 1st time.
* adb binary: $adb (set by 'adb' variable)
* sdcard:     $sd (SD card folder in your device)
* _2or3:      $_2or3 (set '3' or else for python3)
* arch:       $arch (not-set: arm, set '_x86', '_mips' or else)
* nosu:       $nosu (not-set: use su, set: not use su for emulator)
EOF
[ x$sd = x ] && echo you must specify your sd card from sd && exit 1
[ x$adb = x ] && adb=adb
[ x$_2or3 != x ] && _2or3=3
sdext=/sdcard           # fix to fit your devcie.
zip_bin=python${_2or3}_$(cat LATEST_VERSION)$arch.zip
zip_ext=python${_2or3}_extras_$(cat LATEST_VERSION_EXTRA).zip
pkg=com.googlecode.python${_2or3}forandroid
path_inst=$sd/$pkg
path_app=/data/data/$pkg/files

$adb push $zip_bin $path_inst
$adb push $zip_ext $path_inst
for i in python-scripts/*.py; do
    $adb push $i $sd/sl4a/scripts; done
# you need root permission with it
if [ x$nosu = x ]; then
    $adb shell "su -c \"cd $path_app; rm -r python; unzip -o $path_inst/$zip_bin\""
    $adb shell "su -c \"cd $path_inst; rm -r extras; mkdir extras; cd extras; unzip -o ../$zip_ext\""
else
    $adb shell "cd $path_app; rm -r python; unzip -o $path_inst/$zip_bin"
    $adb shell "cd $path_inst; rm -r extras; mkdir extras; cd extras; unzip -o ../$zip_ext"
fi

