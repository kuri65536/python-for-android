#!/bin/bash

# This script will prepare setuptools to be build for Android platform

PACKAGE="setuptools"
VERSION="0.6c11"
URL="https://pypi.python.org/packages/source/s"

if [ ! -f ${PACKAGE}-${VERSION}.tar.gz ]; then
    wget -O ${PACKAGE}-${VERSION}.tar.gz $URL/${PACKAGE}/${PACKAGE}-${VERSION}.tar.gz
fi

rm -rf ${PACKAGE}
tar -xzvf ${PACKAGE}-${VERSION}.tar.gz
mv ${PACKAGE}-${VERSION} ${PACKAGE}
pushd ${PACKAGE}

for i in $(cat ../setuptools.deletes); do
    rm -rf $i
done

for i in $(ls ../setuptools*.patch); do
    patch -p1 -i ../$i
done

popd
