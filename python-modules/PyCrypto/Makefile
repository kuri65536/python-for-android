# Copyright 2017 Shimoda (kuri65536 at hotmail dot com)
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
VERSION := 2.6.1
NAME := pycrypto
URL := http://ftp.dlitz.net/pub/dlitz/crypto/pycrypto
# URL=https://ftp.dlitz.net/pub/dlitz/crypto/pycrypto/pycrypto-2.6.1.tar.gz

# settings {{{1
SRCDIR := $(NAME)-$(VERSION)
SRCTGZ := $(NAME)-$(VERSION).tar.gz

DISTWHL = $(NAME)-$(VERSION)-$(PYVER)-$(PYABI)-$(PYTHON_PLATNAME).whl


ifeq (x$(NDK_PATH),x)
    errmsg := "NDK_PATH is null"
endif

PY4A_SRC := $(abspath ../..)

ifeq (x$(PY),x2)
    # python2 is not maintained, now.
    PYTHON_FOR_BUILD := $(PY4A_SRC)/python-build/host/bin/python
    pylib=$PY4A_SRC/python-build/python_arm/python/lib
    opt_setup=

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

    BUILDMACHINE := $(shell uname -m)
    BUILDOS := $(shell uname -s | tr A-Z a-z)
    BUILDARCH := $(BUILDMACHINE)-$(BUILDOS)-gnu
    ifeq (x$(host),x)
        # check host variable: linux-x86_64, linux-x86 or darwin-x86
        host := $(BUILDOS)-$(BUILDMACHINE)
    endif

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

export ANDROID_TOOLCHAIN := $(NDK_PATH)/toolchains/$(tabi)/prebuilt/$(host)/bin
export PATH := $(ANDROID_TOOLCHAIN):$(PATH)

# build settings section 2 {{{1
ANDROID_NDK_ROOT := $(NDK_PATH)
export ANDROID_SYSROOT := $(NDK_PATH)/platforms/$(ANDROID_API)/$(_ANDROID_ARCH)

# Is it not needed?
# if [ x$ANDROID_NDK_TOOLCHAIN_ROOT = x ]; then
#     echo "ANDROID_NDK_TOOLCHAIN_ROOT is null"
#     exit 1
# fi
ifeq (x$(errmsg),x)
    all: build
else
    all: error
endif

.PHONY: build error clean

error:
	@echo $(errmsg)

build: $(DISTWHL)

clean:
	rm -rf $(DISTWHL) $(SRCDIR)

$(SRCTGZ):
	wget -O $@ ${URL}/${NAME}-${VERSION}.tar.gz

$(SRCDIR): $(SRCTGZ)
	rm -rf $@
	tar -xvzf $<
	cd $@; \
	for i in ../*.patch; do \
	    patch -p1 -i $$i; \
	done
	cp -r $(PY4A_SRC)/python-build/python-libs/py4a $@/
	cp __main__.py $@/py4a
	touch $@

$(DISTWHL): $(SRCDIR)
	@echo build $@
	cd $< ;\
	ac_cv_func_malloc_0_nonnull=yes \
	  $(PYTHON_FOR_BUILD) $(opt_setup) setup.py bdist_wheel \
	    --plat-name=$(PYTHON_PLATNAME) --dist-dir ..

# end of file {{{1
# vi: ft=make:ts=4:et:nowrap:fdm=marker
