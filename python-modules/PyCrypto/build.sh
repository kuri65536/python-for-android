#!/bin/bash # build script for pycrypto for Py4a
if [ x$ANDROID_NDK = x ]; then
    echo "ANDROID_NDK is null"
    exit 1
fi
PY4A_SRC=$(realpath ../..)
if [ x$PY = x2 ]; then
    hostpython=$PY4A_SRC/python-build/host/bin/python
    pylib=$PY4A_SRC/python-build/python_arm/python/lib
    opt_setup=
elif [ x$PY = x3 ]; then
    hostpython=$PY4A_SRC/python3-alpha/host/bin/python3
    pylib=$PY4A_SRC/python3-alpha/python3_arm/python3/lib

    PYSUB=3.6
    PYHOST=linux-armv
    ARCH=arm
    BUILDMACHINE=$(uname -m)
    BUILDOS=$(uname -s | tr A-Z a-z)
    BUILD=$BUILDOS-$BUILDMACHINE

    BINPATH=$ANDROID_NDK/toolchains/arm-linux-androideabi-4.9
    export PATH=$BINPATH/prebuilt/$BUILD/bin:$PATH

    export PY4A=$PY4A_SRC/python3-alpha/python3_$ARCH/python3
    export PY4A_ROOT=$ANDROID_NDK/platforms/android-9/arch-arm
    export PY4A_INC=$PY4A/include/python${PYSUB}m
    export PY4A_LIB=$PY4A/lib
    opt_setup="-m py4a"
else
    echo "PY is null, specify 2 or 3"
    exit 1
fi
# Is it not needed?
# if [ x$ANDROID_NDK_TOOLCHAIN_ROOT = x ]; then
#     echo "ANDROID_NDK_TOOLCHAIN_ROOT is null"
#     exit 1
# fi

VERSION=2.6.1
NAME=pycrypto
URL=http://ftp.dlitz.net/pub/dlitz/crypto/pycrypto
# URL=https://ftp.dlitz.net/pub/dlitz/crypto/pycrypto/pycrypto-2.6.1.tar.gz

if [ ! -f ${NAME}-${VERSION}.tar.gz ]; then
  wget -O ${NAME}-${VERSION}.tar.gz ${URL}/${NAME}-${VERSION}.tar.gz
fi

if [ ! -d ${NAME}-${VERSION} ]; then
  rm -rf ${NAME}-${VERSION}
  tar -xvzf ${NAME}-${VERSION}.tar.gz
  pushd ${NAME}-${VERSION}
  for i in $(ls ../*.patch); do
    patch -p1 -i $i
  done
  popd
fi

pushd ${NAME}-${VERSION}
ln -sf $PY4A_SRC/python-build/python-libs/py4a .
# source $(pwd)/../../python/bin/setup.sh
export ac_cv_func_malloc_0_nonnull=yes
# $hostpython $opt_setup setup.py build_ext --plat-name=linux-armv \
#                           --library-dirs=$pylib
# $hostpython $opt_setup setup.py bdist_egg
# $hostpython $opt_setup setup.py build
$hostpython $opt_setup setup.py bdist_wheel

