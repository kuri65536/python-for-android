pushd ../thirdparty
export THIRD_PARTY_DIR=`pwd`
popd

make HOSTPYTHON=./hostpython HOSTPGEN=./Parser/hostpgen BLDSHARED="arm-linux-androideabi-gcc -shared" CROSS_COMPILE=arm-linux-androideabi- CROSS_COMPILE_TARGET=yes HOSTARCH=arm-linux-androideabi BUILDARCH=x86_64-linux-gnu && \
make install HOSTPYTHON=./hostpython BLDSHARED="arm-linux-androideabi-gcc -shared" CROSS_COMPILE=arm-linux-androideabi- CROSS_COMPILE_TARGET=yes prefix=${PWD}/_install/python3 &&\
./xpack.sh
