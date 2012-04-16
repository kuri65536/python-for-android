#! /usr/bin/python

# Copyright (C) 2011 Naranjo Manuel Francisco <manuel@aircable.net>
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not
# use this file except in compliance with the License. You may obtain a copy of
# the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations under
# the License.

#
# A script that needs to be run every time we rebuild the Python VM for Android
# it will put all the .so files into the apk and generate the proper files.xml
#

import zipfile, os
from re import compile

def work():
    dyn_match = compile("(?P<path>.*)/(?P<name>.*)")
    path = compile("python/(?P<path>.*)")

    BIN_VERSION=open("LATEST_VERSION").read().strip()
    EXTRA_VERSION=open("LATEST_VERSION_EXTRA").read().strip()
    os.system("mkdir -p ../android/PythonForAndroidInOne/res/raw/")
    os.system("mkdir -p ../android/PythonForAndroidInOne/libs/armeabi")
    XML=open("../android/PythonForAndroidInOne/res/raw/files.xml", "w")
    ARMEABI="../android/PythonForAndroidInOne/libs/armeabi/"
    
    os.system("rm %s/*.so" % ARMEABI)

    XML.write('<?xml version="1.0" encoding="UTF-8"?>\n')
    XML.write('<files>\n')
    i = 0
    z = zipfile.ZipFile("python_%s.zip" % BIN_VERSION)
    for f in z.filelist:
        g = dyn_match.match(f.filename).groupdict()
        XML.write('<file src="lib%04i.so" target="%s"/>\n' % (i, path.findall(f.filename)[0]))
        f.filename = "lib%04i.so" % i
        print z.extract(f, ARMEABI)
        i=i+1

    XML.write('<file src="lib%04i.so" target="lib/python2.6/python.zip"/>\n' % i)
    XML.write('</files>\n')
    os.system("cp python_extras_%s.zip %s/lib%04i.so" % ( EXTRA_VERSION, ARMEABI, i ) )
    XML.close()

if __name__=='__main__':
    work()
