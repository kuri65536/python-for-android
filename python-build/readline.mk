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

# This makefile builds both for host and target, and so all the
# common definitions are factored out into a separate file to
# minimize duplication between the build rules.

LOCAL_PATH := $(call my-dir)/lib-$(TARGET_ARCH_ABI)

# pre-build
.PHONY: build_arm build_x86

BUILDMACHINE := $(shell uname -m)
BUILDOS := $(shell uname -s | tr A-Z a-z)
NDK_BUILDARCH := $(BUILDOS)-$(BUILDMACHINE)
BUILDARCH := $(BUILDMACHINE)-pc-$(BUILDOS)-gnu
OPTS_CFG = --host=$(HOSTARCH) --build=$(BUILDARCH) \
           --prefix=$(READLINE_PATH)/lib-$(TARGET_ARCH_ABI) \
           --enable-shared --disable-static \
           --with-curses=$(NCURSES_PATH)/lib-$(TARGET_ARCH_ABI)/python \
           --enable-multibyte

export CFLAGS = -DANDROID --sysroot=$(SYSROOT) \
                -I$(NCURSES_PATH)/lib-$(TARGET_ARCH_ABI)/python/include \
                -fPIE -fvisibility=default
export LDFLAGS = --sysroot=$(SYSROOT) \
                -L$(NCURSES_PATH)/lib-$(TARGET_ARCH_ABI)/python/lib \
                -rdynamic -fPIE -lncurses -ltinfo

build_arm: export HOSTARCH := arm-linux-androideabi
build_arm: export PATH := $(NDK_PATH)/toolchains/arm-linux-androideabi-4.9/prebuilt/$(NDK_BUILDARCH)/bin:$(PATH)
build_arm: export SYSROOT := $(NDK_PATH)/platforms/android-3/arch-arm
build_arm:
	make clean || echo 0
	autoreconf -i; \
	bash_cv_wcwidth_broken=no \
	./configure $(OPTS_CFG)
	make
	make install
	cd lib-$(TARGET_ARCH_ABI)/lib; chmod 755 *.so*


build_x86: export HOSTARCH := i686-linux-android
build_x86: export PATH := $(NDK_PATH)/toolchains/x86-4.9/prebuilt/$(NDK_BUILDARCH)/bin:$(PATH)
build_x86: export SYSROOT := $(NDK_PATH)/platforms/android-9/arch-x86
build_x86:
	make clean || echo 0
	autoreconf -i; \
	bash_cv_wcwidth_broken=no \
	./configure $(OPTS_CFG)
	make
	make install
	cd lib-$(TARGET_ARCH_ABI)/lib; chmod 755 *.so*

include $(CLEAR_VARS)
LOCAL_MODULE := readline
LOCAL_SRC_FILES := $(LOCAL_PATH)/lib/libreadline.so
LOCAL_C_INCLUDES := $(LOCAL_PATH)/include
include $(PREBUILT_SHARED_LIBRARY)

include $(CLEAR_VARS)
LOCAL_MODULE := history
LOCAL_SRC_FILES := $(LOCAL_PATH)/lib/libhistory.so
LOCAL_C_INCLUDES := $(LOCAL_PATH)/include
include $(PREBUILT_SHARED_LIBRARY)

