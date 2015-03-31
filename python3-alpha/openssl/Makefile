export ANDROID_NDK_ROOT := $(NDK_PATH)

export HOSTCC := gcc
export RELEASE := 2.6.37
export SYSTEM := android

export ANDROID_SYSROOT=$(NDK_PATH)/platforms/$(ANDROID_API)/$(_ANDROID_ARCH)
export SYSROOT=$(ANDROID_SYSROOT)
export NDK_SYSROOT=$(ANDROID_SYSROOT)
export ANDROID_NDK_SYSROOT=$(ANDROID_SYSROOT)
export ANDROID_DEV=$(ANDROID_SYSROOT)/usr
# export PATH=$(ANDROID_TOOLCHAIN):$(PATH)

OPENSSL_VERSION := 1.0.2a
OPENSSL_DIR = openssl-$(OPENSSL_VERSION)
OPENSSL_SRC = openssl-$(OPENSSL_VERSION).tar.gz

OPENSSL_BIN_x86 := .build_x86/libcrypto.so \
                   .build_x86/libssl.so
OPENSSL_BIN_arm := .build_arm/libcrypto.so \
                   .build_arm/libssl.so
OPENSSL_BIN := $(OPENSSL_BIN_x86) $(OPENSSL_BIN_arm)

eabi_arm := arm-linux-androideabi-4.9
eabi_x86 := x86-4.9

perlopt := -pi -e 's/install: all install_docs install_sw/install: install_sw/g'

ifeq (x$(host),x)
# check host variable: linux-x86_64, linux-x86 or darwin-x86
host = $(shell uname -s | tr A-Z a-z)-$(shell uname -m)
endif
ifeq (x$(PYBIN),x)
build: error
else
build: $(OPENSSL_BIN)
	ln -sf .build_arm openssl-src
endif

.PHONY: build clean cleanall

error:
	echo PYBIN must be defined.

cleanall: clean
	rm -f $(OPENSSL_SRC)

clean:
	make -C .build_arm clean
	make -C .build_x86 clean

$(OPENSSL_SRC):
	wget https://www.openssl.org/source/openssl-1.0.2a.tar.gz
	wget https://wiki.openssl.org/images/7/70/Setenv-android.sh

# setup arch depended variables: arm
$(OPENSSL_BIN_arm): export ANDROID_API := android-4
$(OPENSSL_BIN_arm): \
    export ANDROID_TOOLCHAIN=$(NDK_PATH)/toolchains/$(eabi_arm)/prebuilt/$(host)/bin
$(OPENSSL_BIN_arm): export PATH:=$(ANDROID_TOOLCHAIN):$(PATH)
$(OPENSSL_BIN_arm): export _ANDROID_ARCH=arch-arm
$(OPENSSL_BIN_arm): export _ANDROID_EABI=$(eabi_arm)
$(OPENSSL_BIN_arm): export MACHINE=armv7
$(OPENSSL_BIN_arm): export ARCH=arm
$(OPENSSL_BIN_arm): export CROSS_COMPILE="arm-linux-androideabi-"
$(OPENSSL_BIN_arm): \
    export ANDROID_TOOLS="arm-linux-androideabi-gcc arm-linux-androideabi-ranlib arm-linux-androideabi-ld"

$(OPENSSL_BIN_arm): .build_arm
	./showenv.sh
	cd $<; perl $(perlopt) Makefile.org
	cd $<; ./config shared no-ssl2 no-ssl3 no-comp no-hw no-engine \
	  --openssldir=$(PYBIN)/share --prefix=$(PYBIN)
	make -C $< depend
	make -C $< all
	make -C $< install_sw

# setup arch depended variables: x86
$(OPENSSL_BIN_x86): export ANDROID_API := android-9
$(OPENSSL_BIN_x86): \
    export ANDROID_TOOLCHAIN=$(NDK_PATH)/toolchains/$(eabi_x86)/prebuilt/$(host)/bin
$(OPENSSL_BIN_x86): export PATH:=$(ANDROID_TOOLCHAIN):$(PATH)
$(OPENSSL_BIN_x86): export _ANDROID_ARCH=arch-x86
$(OPENSSL_BIN_x86): export _ANDROID_EABI=$(eabi_x86)
$(OPENSSL_BIN_x86): export MACHINE=i686
$(OPENSSL_BIN_x86): export ARCH=x86
$(OPENSSL_BIN_x86): export CROSS_COMPILE="i686-linux-android-"
$(OPENSSL_BIN_x86): export PATH:=$(ANDROID_TOOLCHAIN):$(PATH)
$(OPENSSL_BIN_x86): \
    export ANDROID_TOOLS="i686-linux-android-gcc arm-linux-androideabi-ranlib arm-linux-androideabi-ld"

$(OPENSSL_BIN_x86): .build_x86
	./showenv.sh
	cd $<; perl $(perlopt) Makefile.org
	cd $<; ./config shared no-ssl2 no-ssl3 no-comp no-hw no-engine \
	  --openssldir=$(NDK_PATH)/platforms/$(ANDROID_API)/arch-arm/usr/local/ssl/
	make -C $< depend
	make -C $< all

.build_x86: $(OPENSSL_SRC)
	tar xfz $(OPENSSL_SRC)
	mv $(OPENSSL_DIR) .build_x86

.build_arm: $(OPENSSL_SRC)
	tar xfz $(OPENSSL_SRC)
	mv $(OPENSSL_DIR) .build_arm

