# Copyright 2017, 2015 Shimoda (kuri65536 at hotmail dot com)
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
VERSION := 17.1.0
NAME := Twisted
URL = https://files.pythonhosted.org/packages/source/T/Twisted/$(SRCARC)

# settings {{{1
SRCDIR := $(NAME)-$(VERSION)
SRCARC := $(NAME)-$(VERSION).tar.bz2
ARCOPTS := xjf

DISTWHL = $(NAME)-$(VERSION)-$(PYVER)-$(PYABI)-$(PYTHON_PLATNAME).whl


ifeq (x$(NDK_PATH),x)
    errmsg := "NDK_PATH is null"
endif

## python 2 or 3 {{{2
PY4A_SRC := $(abspath ../..)

ifeq (x$(ARCH),xx86)
    errmsg += x86 arch is not supported, now.  #

else
    ARCH := arm
    PYHOST := linux-armv
endif

ifeq (x$(PY),x2)
    # python2 is not maintained, now.
    PYSUB := 2.7

    export PY4A_ := $(PY4A_SRC)/python-build/python
    export PY4A_ROOT := $(ANDROID_NDK)/platforms/android-3/arch-arm
    export PY4A := $(PY4A_SRC)/python-build/python
    PYTHON_FOR_BUILD := $(PY4A_SRC)/python-build/host/bin/python

else ifeq (x$(PY),x3)
    PYTHON_PLATNAME := linux-armv7l
    export _PYTHON_HOST_PLATFORM := arm-linux-androideabi
    export EXT_SUFFIX := .cpython-36m-$(_PYTHON_HOST_PLATFORM).so
    export SOABI := cpython-36m-arm-linux-androideabi
    PYTHON_FOR_BUILD := $(PY4A_SRC)/python3-alpha/host/bin/python3
    pylib := $(PY4A_SRC)/python3-alpha/python3_arm/python3/lib

    VER_MAJ := 3.6
    PYVER := cp36
    PYABI := cp36m
    ARCH=arm

    TARGET := arm-linux-androideabi
    tabi := $(TARGET)-4.9
    _ANDROID_ARCH = arch-arm

    PY4A := $(PY4A_SRC)/python3-alpha/python3_$(ARCH)/python3
    export PY4A_INC := $(PY4A)/include/python$(VER_MAJ)m
    export PY4A_LIB := $(PY4A)/lib
    opt_setup := -m py4a
    export ANDROID_API := android-9

    export PYTHONSRC := $(PY4A_SRC)/python3-alpha/python-src_arm

else
    errmsg += ", PY is null, specify 2 or 3"
endif

# build variables {{{1
# PWD for py4a module
# export PYTHONPATH := $(PYTHONPATH):$(PWD)

BUILDMACHINE := $(shell uname -m)
BUILDOS := $(shell uname -s | tr A-Z a-z)
BUILDARCH := $(BUILDMACHINE)-$(BUILDOS)-gnu
BUILD := $(BUILDOS)-$(BUILDMACHINE)
ifeq (x$(host),x)
    # check host variable: linux-x86_64, linux-x86 or darwin-x86
    host := $(BUILDOS)-$(BUILDMACHINE)
endif

ifeq (x$(ARCH),xx86)
    export CC := 
else
    #these are set in py4a/__init__.py
    # export CC := arm-linux-androideabi-gcc --sysroot=$(PY4A_ROOT)
    # export CFLAGS := -mtune=xscale -march=armv5te -msoft-float
endif

# build settings section 2 {{{1
ANDROID_NDK_ROOT := $(NDK_PATH)
export ANDROID_SYSROOT := $(NDK_PATH)/platforms/$(ANDROID_API)/$(_ANDROID_ARCH)
export ANDROID_TOOLCHAIN := $(NDK_PATH)/toolchains/$(tabi)/prebuilt/$(host)/bin
export PATH := $(ANDROID_TOOLCHAIN):$(PATH)


ifeq (x$(errmsg),x)
    all: build
else
    all: error
endif

# build rules {{{1
.PHONY: all error build clean

error:
	@echo $(errmsg)

build: $(DISTWHL)

clean:
	rm -rf $(DISTWHL) $(SRCDIR)

$(SRCARC):
	wget -O $@ $(URL)

$(SRCDIR): $(SRCARC)
	rm -rf $@
	tar $(ARCOPTS) $<
	cp -r  $(PY4A_SRC)/python-build/python-libs/py4a $@/
	cd $@/py4a; ln -sf ../../__main__.py .
	# cd $@; for i in $(PWD)/*.patch; do patch -p1 -i $$i; done
	touch $@

#these are set in py4a/__init__.py
# export CFLAGS += --sysroot=$(NDK_SYSROOT) -DANDROID \
#                  -fPIE -fvisibility=default
# export CXXFLAGS = $(CFLAGS)
# export CPPFLAGS = $(CFLAGS)
# export LDFLAGS := --sysroot=$(NDK_SYSROOT) \
#                   -rdynamic -fPIE
# export LDSHARED := $(LDFLAGS)


depend:
	pip download incremental
	$(PYTHON_FOR_BUILD) -m pip install incremental*.whl
	touch $`


$(DISTWHL): $(SRCDIR) depend
	# cd $(dir $<); python setup.py --help; exit 1
	# invalid: --plat-name=linux-armv
	@echo these might be null, are set by py4a/__init__.py
	@echo PATH    : $(PATH)
	@echo CC      : $(CC)
	@echo CFLAGS  : $(CFLAGS)
	@echo CPPFLAGS: $(CPPFLAGS)
	@echo CXXFLAGS: $(CXXFLAGS)
	@echo LDFLAGS : $(LDFLAGS)
	@echo LDSHARED: $(LDSHARED)
	@echo PYTHONPATH: $$PYTHONPATH
	arm-linux-androideabi-gcc -v
	cd $<; \
	  $(PYTHON_FOR_BUILD) $(opt_setup) setup.py bdist_wheel \
	    --plat-name=$(PYTHON_PLATNAME) --dist-dir ..
#	  $(HOSTPYTHON) -m py4a setup.py -v build --fcompiler=fake

# end of file {{{1
# vi: ft=make:ts=4:et:nowrap:fdm=marker
