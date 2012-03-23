. ../VERSIONS
ZIPMAIN=python3_r${PY34A_VERSION}.zip
ZIPEXTRA=python3_extras_r${PY34A_EXTRAS_VERSION}.zip
ZIPSCRIPTS=python3_scripts_r${PY34A_SCRIPTS_VERSION}.zip
echo "Packing $ZIPMAIN"
rm $ZIPMAIN
pushd _install
cp ../../thirdparty/lib/libsqlite3.so.0 python3/lib
zip -g ../$ZIPMAIN python3/bin/python3
zip -gri"*.so" -i"*.so.0" ../$ZIPMAIN python3/lib
popd

echo "Packing $ZIPEXTRA"
rm ${ZIPEXTRA}.zip
rm -r android
mkdir android
mkdir android/python3
cp android.py _install/python3/lib/python3.2
cp -r ../extra_modules/* _install/python3/lib/python3.2
cp -r _install/python3/lib/python3.2/* android/python3
pushd android
zip -grx"*.so" -x"*.so.0" ../$ZIPEXTRA python3
zip -d ../$ZIPEXTRA "*.pc" "*pkgconfig*" "*lib/libpython3.2m.a" "*/test/*" "*.a"
popd

echo "Packing $ZIPSCRIPTS"
rm $ZIPSCRIPTS
cd android-scripts
zip -g ../$ZIPSCRIPTS *

