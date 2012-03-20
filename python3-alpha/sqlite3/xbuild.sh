TARGET=arm-linux-androideabi
pushd ../thirdparty
TARGET_DIR=`pwd`
popd

./configure --host=$TARGET --target=$TARGET --prefix=$TARGET_DIR && make && make install

