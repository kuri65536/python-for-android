#!/bin/bash

VERSION="r1"

ndk-build
rm -rf out
mkdir out
cp -r zope out
cp libs/armeabi/*.so out/zope/interface
pushd out
rm ../zope-${VERSION}.zip
zip -r ../zope-${VERSION}.zip .
popd
