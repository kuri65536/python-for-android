pushd ../thirdparty
export THIRD_PARTY_DIR=`pwd`
popd
export TARGET=arm-linux-androideabi

CC=${TARGET}-gcc CXX=${TARGET}-g++ AR=${TARGET}-ar RANLIB=${TARGET}-ranlib ./configure --host=${TARGET} --build=x86_64-linux-gnu --prefix=/python --enable-shared

# make HOSTPYTHON=./hostpython HOSTPGEN=./Parser/hostpgen BLDSHARED="arm-linux-androideabi-gcc -shared" CROSS_COMPILE=arm-linux-androideabi- CROSS_COMPILE_TARGET=yes HOSTARCH=ppc-linux BUILDARCH=x86_64-linux-gnu


