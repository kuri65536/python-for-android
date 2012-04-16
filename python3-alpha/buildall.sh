echo "Building all Py34a"
echo "openssl"
pushd openssl
./xbuild.sh
popd
echo "Sqlite3"
pushd sqlite3
./xbuild.sh
popd
echo "zlip"
pushd zlib-1.2.6
./xbuild.sh
popd
echo "bz2"
pushd bzip2-1.0.6
./xbuild.sh
popd
echo "ncurses"
pushd ncurses-5.9
./xbuild.sh
popd
echo "readline"
pushd readline-6.2
./xbuild.sh
popd
echo "Python 3"
pushd python3-src
./xbuild.sh
popd

echo "And done."
