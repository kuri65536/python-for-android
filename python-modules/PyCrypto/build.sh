#!/bin/bash

# build script for pycrypto for Py4a
if [ x$ANDROID_NDK = x ]; then
    echo "ANDROID_NDK is null"
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
source $(pwd)/../../python/bin/setup.sh
export ac_cv_func_malloc_0_nonnull=yes
python setup.py build_ext --plat-name=linux-armv \
                          --library-dirs=../python/lib
python setup.py bdist_egg

