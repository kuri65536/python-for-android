# Copyright 2015 Shimoda (kuri65536 at hotmail dot com)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# This makefile builds the host binary (egg).
# minimize duplication between the build rules.


# settings {{{1
bin = $(src)/dist/$(src)-py2.7-$(PYHOST).egg
tar := numpy-1.9.2.tar.gz
src := numpy-1.9.2
url := http://downloads.sourceforge.net/project/numpy/NumPy/1.9.2/$(tar)

# numpy-1.9.2/dist/numpy-1.9.2-py2.7-linux-armv.egg
# numpy-1.9.2/build/scripts.linux-x86_64-2.7/f2py
buildend = $(src)/build/scripts.$(BUILD)-2.7/f2py


# build rules {{{1
.PHONY: all error build

ifeq (x$(ANDROID_NDK),x)
    all: error
else
    all: build
endif

build: $(bin)

error:
	echo ANDROID_NDK must be set.

$(tar):
	wget -O $@ $(url)

$(src)/setup.py: $(tar)
	tar xfz $(tar)
	cd $(src); for i in $(PWD)/*.patch; do patch -p1 -i $$i; done
	touch $@

$(buildend): $(src)/setup.py
	# cd $(dir $<); python setup.py --help; exit 1
	# invalid: --plat-name=linux-armv
	@echo these might be null, are set by py4a/__init__.py
	@echo CC      : $(CC)
	@echo CFLAGS  : $(CFLAGS)
	@echo CPPFLAGS: $(CPPFLAGS)
	@echo CXXFLAGS: $(CXXFLAGS)
	@echo LDFLAGS : $(LDFLAGS)
	@echo LDSHARED: $(LDSHARED)
	cd $(dir $<); \
	  $(HOSTPYTHON) setup.py -v build --fcompiler=fake

$(bin): $(buildend)
	@echo build $(bin) from $(buildend)
	$(HOSTPYTHON) check_setuptools.py
	# invalid: --prefix=/mnt/sdcard/com.googlecode.pythonforandroid/extras/python
	cd $(src); \
	  $(HOSTPYTHON) setupegg.py bdist_egg --plat-name=$(PYHOST)


# build variables {{{1
export PY4A := $(PWD)/../python
export PY4A_INC := $(PY4A)/include/python2.7
export PY4A_LIB := $(PY4A)/lib
export PYTHONPATH := $(PY4A_LIB)/python2.7
HOSTPYTHON := $(PWD)/../../python-build/host/bin/python

BUILDMACHINE := $(shell uname -m)
BUILDOS := $(shell uname -s | tr A-Z a-z)
BUILD := $(BUILDOS)-$(BUILDMACHINE)


ifeq (x$(ARCH),xx86)
    export CC := 
else
    PYHOST := linux-armv
    export PY4A_ROOT := $(ANDROID_NDK)/platforms/android-3/arch-arm
    BINPATH := $(ANDROID_NDK)/toolchains/arm-linux-androideabi-4.9
    export PATH := $(BINPATH)/prebuilt/$(BUILD)/bin:$(PATH)
    #these are set in py4a/__init__.py
    # export CC := arm-linux-androideabi-gcc --sysroot=$(PY4A_ROOT)
    # export CFLAGS := -mtune=xscale -march=armv5te -msoft-float
endif

#these are set in py4a/__init__.py
# export CFLAGS += --sysroot=$(NDK_SYSROOT) -DANDROID \
#                  -fPIE -fvisibility=default
# export CXXFLAGS = $(CFLAGS)
# export CPPFLAGS = $(CFLAGS)
# export LDFLAGS := --sysroot=$(NDK_SYSROOT) \
#                   -rdynamic -fPIE
# export LDSHARED := $(LDFLAGS)

# end of file {{{1
# vi: ft=makefile:nowrap:fdm=marker
