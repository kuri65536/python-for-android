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

# This makefile builds the two archtechture shared libraries.
# minimize duplication between the build rules.

LOCAL_PATH := $(call my-dir)/lib-$(TARGET_ARCH_ABI)/python

# pre-build
.PHONY: build_arm build_x86

BUILDMACHINE := $(shell uname -m)
BUILDOS := $(shell uname -s | tr A-Z a-z)
NDK_BUILDARCH := $(BUILDOS)-$(BUILDMACHINE)
BUILDARCH := $(BUILDMACHINE)-pc-$(BUILDOS)-gnu
__APPPATH := /data/data/com.googlecode.pythonforandroid/files
__TERMPATH := $(__APPPATH)/python/share/terminfo
OPTS_CFG = --host=$(HOSTARCH) --build=$(BUILDARCH) \
    --prefix=/python \
    --with-install-prefix=$(NCURSES_PATH)/lib-$(TARGET_ARCH_ABI) \
    --with-shared --without-normal \
    --disable-rpath \
    --without-ada --without-cxx --without-manpages \
    --without-progs --without-tests \
    --with-termlib --enable-termcap \
    --disable-home-terminfo \
    --with-default-terminfo-dir=$(__TERMPATH) \
    --with-terminfo-dirs=$(__TERMPATH)
export CFLAGS = --sysroot=$(SYSROOT) -DANDROID
export CPPFLAGS = -P
export LDFLAGS = --sysroot=$(SYSROOT)

build_arm: export HOSTARCH := arm-linux-androideabi
build_arm: export PATH := $(NDK_PATH)/toolchains/arm-linux-androideabi-4.9/prebuilt/$(NDK_BUILDARCH)/bin:$(PATH)
build_arm: export SYSROOT := $(NDK_PATH)/platforms/android-3/arch-arm
build_arm:
	make clean || echo
	./configure $(OPTS_CFG)
	make
	make install
	cd lib-$(TARGET_ARCH_ABI)/include; ln -sf ncurses/curses.h .
	cd lib-$(TARGET_ARCH_ABI)/include; ln -sf ncurses/panel.h .
	# not worked...
	# cd lib-$(TARGET_ARCH_ABI)/lib; for i in *.so*; do \
	#   [ -L $$i ] && cp --remove-destination `readlink $$i` $$i; done; echo

build_x86: export HOSTARCH := i686-linux-android
build_x86: export PATH := $(NDK_PATH)/toolchains/x86-4.9/prebuilt/$(NDK_BUILDARCH)/bin:$(PATH)
build_x86: export SYSROOT := $(NDK_PATH)/platforms/android-9/arch-x86
build_x86:
	make clean || echo
	./configure $(OPTS_CFG)
	make
	make install
	cd lib-$(TARGET_ARCH_ABI)/include; ln -sf ncurses/curses.h .
	cd lib-$(TARGET_ARCH_ABI)/include; ln -sf ncurses/panel.h .


include $(CLEAR_VARS)
LOCAL_MODULE := ncurses
LOCAL_SRC_FILES := $(LOCAL_PATH)/lib/libncurses.so
LOCAL_EXPORT_C_INCLUDES := $(LOCAL_PATH)/include $(LOCAL_PATH)/include/ncurses
include $(PREBUILT_SHARED_LIBRARY)

include $(CLEAR_VARS)
LOCAL_MODULE := termcap
LOCAL_SRC_FILES := $(LOCAL_PATH)/lib/libtinfo.so
include $(PREBUILT_SHARED_LIBRARY)

include $(CLEAR_VARS)
LOCAL_MODULE := ncurses_panel
LOCAL_SRC_FILES := $(LOCAL_PATH)/lib/libpanel.so
include $(PREBUILT_SHARED_LIBRARY)

