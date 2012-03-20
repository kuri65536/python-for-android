TARGET=arm-linux-androideabi
pushd ../thirdparty
export TARGET_DIR=`pwd`
popd

make && make install

