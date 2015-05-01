#! /bin/bash
cat <<EOF
* you should have rooted phone.
* you must click 1st time.
* adb:    $adb
* sdcard: $sd in your device.
* _2or3:  $_2or3
EOF
[ x$sd = x ] && (echo you must specify your sd card from sd; exit 1)
[ x$adb = x ] && adb=adb
sdext=/sdcard           # fix to fit your devcie.
zip_bin=python${_2or3}_$(cat LATEST_VERSION).zip
zip_ext=python${_2or3}_extras_$(cat LATEST_VERSION_EXTRA).zip
pkg=com.googlecode.python${_2or3}forandroid
path_inst=$sd/$pkg
path_app=/data/data/$pkg/files

$adb push $zip_bin $path_inst
$adb push $zip_ext $path_inst
# you need root permission with it
$adb shell "su -c \"cd $path_app; rm -r python; unzip -o $path_inst/$zip_bin\""
$adb shell "su -c \"cd $path_inst; rm -r extras; mkdir extras; cd extras; unzip -o ../$zip_ext\""

