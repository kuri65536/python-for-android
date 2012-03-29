export 	TARGET=arm-linux-androideabi
pushd ../thirdparty
TARGET_DIR=`pwd`
popd

LDFLAGS=-L${TARGET_DIR}/lib CFLAGS="-I${TARGET_DIR}/include -I${TARGET_DIR}/include/ncurses" ./configure --host=$TARGET --target=$TARGET --prefix=$TARGET_DIR --enable-shared  --with-curses && \
 patch <android.patch && \
 make && \
 make install

