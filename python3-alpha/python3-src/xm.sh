make HOSTPYTHON=./hostpython HOSTPGEN=./Parser/hostpgen BLDSHARED="arm-linux-androideabi-gcc -shared" CROSS_COMPILE=arm-linux-androideabi- CROSS_COMPILE_TARGET=yes HOSTARCH=ppc-linux BUILDARCH=x86_64-linux-gnu

make install HOSTPYTHON=./hostpython BLDSHARED="arm-linux-androideabi-gcc -shared" CROSS_COMPILE=arm-linux-androideabi- CROSS_COMPILE_TARGET=yes prefix=~/Python-3.2.2/_install/python3
