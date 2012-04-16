TARGET=arm-linux-androideabi
pushd ../thirdparty
TARGET_DIR=`pwd`
popd
export TARGET,TARGET_DIR

make && make install PREFIX=$TARGET_DIR

