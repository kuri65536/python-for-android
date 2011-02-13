#!/bin/bash

VERSION="r1"

ndk-build
rm -rf out
mkdir out
cp -r twisted out
cp libs/armeabi/_epoll.so _initgroups.so out/twisted/python
cp libs/armeabi/_sigchld.so out/twisted/internet
cp libs/armeabi/_c_urlarg.so out/twisted/protocols
cp libs/armeabi/raiser.so out/twisted/test
pushd out
rm ../twisted-${VERSION}.zip
zip -r ../twisted-${VERSION}.zip .
popd
