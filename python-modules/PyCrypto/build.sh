#!/bin/bash

# build script for pycrypto for Py4a

VERSION=2.3
NAME=pycrypto
URL=http://ftp.dlitz.net/pub/dlitz/crypto/pycrypto

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
source ../../python-lib/setup.sh
python setup.py bdist
python setup.py bdist_egg
