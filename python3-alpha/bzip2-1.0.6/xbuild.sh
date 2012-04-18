export TARGET=arm-linux-androideabi
pushd ../thirdparty
export TARGET_DIR=`pwd`
popd

make && make install PREFIX=$TARGET_DIR

