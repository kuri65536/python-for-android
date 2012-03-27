export TARGET=arm-linux-androideabi
pushd ../thirdparty
TARGET_DIR=`pwd`
popd
./configure --host=$TARGET --target=$TARGET --prefix=$TARGET_DIR && \
patch -p1 <android.patch && \
make && \
make install

