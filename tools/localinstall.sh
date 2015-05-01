#! /bin/bash
cat <<EOF
* you should have rooted phone.
* you must click 1st time.
* adb: $adb
* sdcard: $sd in your device.
EOF
[ x$sd = x ] && (echo you must specify your sd card from sd; exit 1)
[ x$adb = x ] && adb=adb
sdext=/sdcard           # fix to fit your devcie.
zip_bin=python_$(cat LATEST_VERSION).zip
zip_ext=python_extras_$(cat LATEST_VERSION_EXTRA).zip
pkg=com.googlecode.pythonforandroid
path_inst=$sd/$pkg
path_app=/data/data/$pkg/files

$adb push $zip_bin $path_inst
$adb push $zip_ext $path_inst
# you need root permission with it
$adb shell "su -c \"cd $path_app; rm -r python; unzip -o $path_inst/$zip_bin\""
$adb shell "su -c \"cd $path_inst; rm -r extras; mkdir extras; cd extras; unzip -o ../$zip_ext\""

