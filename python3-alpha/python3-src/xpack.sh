VERSION=1
ZIPMAIN=python3_r${VERSION}.zip
ZIPEXTRA=python3_extras_r${VERSION}.zip
ZIPSCRIPTS=python3_scripts_r${VERSION}.zip
echo "Packing $ZIPMAIN"
rm $ZIPMAIN
cd _install
cp ../sqlite3/lib/libsqlite3.so.0 python3/lib
zip -g ../$ZIPMAIN python3/bin/python3
zip -gri"*.so" -i"*.so.0" ../$ZIPMAIN python3/lib

echo "Packing $ZIPEXTRA"
rm ../${ZIPEXTRA}.zip
cp ../android.py lib/python3.2
zip -grx"*.so" -x"*.so.0" ../$ZIPEXTRA python3/lib
zip -d ../$ZIPEXTRA "*.pc" "*pkgconfig*" "*lib/libpython3.2m.a" "*/test/*" "*.a"


echo "Packing $ZIPSCRIPTS"
cd ..
rm $ZIPSCRIPTS
cd android-scripts
zip -g ../$ZIPSCRIPTS *

