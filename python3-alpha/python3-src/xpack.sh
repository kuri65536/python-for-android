. ../VERSIONS
ZIPMAIN=python3_r${PY34A_VERSION}.zip
ZIPEXTRA=python3_extras_r${PY34A_EXTRAS_VERSION}.zip
ZIPSCRIPTS=python3_scripts_r${PY34A_SCRIPTS_VERSION}.zip
echo "Packing $ZIPMAIN"
rm $ZIPMAIN
pushd _install
cp ../../thirdparty/lib/libsqlite3.so.0 python3/lib
cp ../../thirdparty/lib/libreadline.so.6 python3/lib
cp ../../thirdparty/lib/libncurses.so.5 python3/lib
cp ../../thirdparty/lib/libz.so.1 python3/lib
#Symbolic linked libs just take up space
find python3/lib -type l -exec rm -f {} \;
zip -g ../$ZIPMAIN python3/bin/python3
zip -gri"*.so" -i"*.so.*" ../$ZIPMAIN python3/lib
zip -g ../$ZIPMAIN python3/lib/python3.2/config-3.2m/Makefile python3/include/python3.2m/pyconfig.h
popd

echo "Packing $ZIPEXTRA"
rm ${ZIPEXTRA}
rm -rf android
mkdir android
mkdir android/python3
cp android.py _install/python3/lib/python3.2
cp -r ../extra_modules/* _install/python3/lib/python3.2
cp -r _install/python3/lib/python3.2/* android/python3
mkdir -p android/python3/terminfo/x
mkdir -p android/python3/terminfo/v
mkdir -p android/python3/terminfo/a
cp ../thirdparty/share/terminfo/x/xterm android/python3/terminfo/x
cp ../thirdparty/share/terminfo/a/ansi android/python3/terminfo/a
cp ../thirdparty/share/terminfo/v/vt320 android/python3/terminfo/v
pushd android
zip -grx"*.so" -x"*.so.*" ../$ZIPEXTRA python3
zip -d ../$ZIPEXTRA "*.pc" "*pkgconfig*" "*lib/libpython3.2m.a" "*/test/*" "*.a"
popd
pushd _install
zip -g ../$ZIPEXTRA python3/lib/python3.2/config-3.2m/Makefile python3/lib/python3.2/site-packages/*
popd

echo "Packing $ZIPSCRIPTS"
rm $ZIPSCRIPTS
cd android-scripts
zip -g ../$ZIPSCRIPTS *

