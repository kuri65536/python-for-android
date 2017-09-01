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

OPENSSL_SERIES := 1.0.2
OPENSSL_RELEASE := j
OPENSSL_VERSION := $(OPENSSL_SERIES)$(OPENSSL_RELEASE)
OPENSSL_DIR = openssl-$(OPENSSL_VERSION)
OPENSSL_SRC = openssl-$(OPENSSL_VERSION).tar.gz

OPENSSL_BIN_x86 := .build_x86/libcrypto.so \
                   .build_x86/libssl.so
OPENSSL_BIN_arm := .build_armeabi/libcrypto.so \
                   .build_armeabi/libssl.so
OPENSSL_BIN := $(OPENSSL_BIN_x86) $(OPENSSL_BIN_arm)

eabi_arm := arm-linux-androideabi-4.9
eabi_x86 := x86-4.9

# this cause CFLAGS to -fPIC ... -fPIE => -fPIE
__PIE_CFLAGS := -fvisibility=default -fPIE

perlopt := -pi -e 's/install: all install_docs install_sw/install: install_sw/g'

ifeq (x$(host),x)
# check host variable: linux-x86_64, linux-x86 or darwin-x86
host = $(shell uname -s | tr A-Z a-z)-$(shell uname -m)
endif
ifeq (x$(PYBINR),x)
build: error
else
build: $(OPENSSL_BIN)
	ln -sf .build_armeabi openssl-src
endif

.PHONY: build clean cleanall

error:
	echo PYBINR must be defined.
	exit 1

cleanall: clean
	rm -f $(OPENSSL_SRC)

clean:
	make -C .build_armeabi clean
	make -C .build_x86 clean


URL1 := https://www.openssl.org/source/$(OPENSSL_SRC)
URL2 := https://www.openssl.org/source/old/$(OPENSSL_SERIES)/$(OPENSSL_SRC)

$(OPENSSL_SRC):
	if wget $(URL1); then \
	    echo; \
	elif wget $(URL2); then \
	    echo; \
	else \
	    echo "can't get $(OPENSSL_SRC)" && exit 1; \
	fi
	wget https://wiki.openssl.org/images/7/70/Setenv-android.sh

# setup arch depended variables: arm
$(OPENSSL_BIN_arm): export ANDROID_API := android-4
$(OPENSSL_BIN_arm): \
    export ANDROID_TOOLCHAIN=$(NDK_PATH)/toolchains/$(eabi_arm)/prebuilt/$(host)/bin
$(OPENSSL_BIN_arm): export PATH:=$(ANDROID_TOOLCHAIN):$(PATH)
$(OPENSSL_BIN_arm): export _ANDROID_ARCH=arch-arm
$(OPENSSL_BIN_arm): export _ANDROID_EABI=$(eabi_arm)
$(OPENSSL_BIN_arm): export MACHINE=armv5te
$(OPENSSL_BIN_arm): export ARCH=arm
$(OPENSSL_BIN_arm): PREFIX=$(CWD)/$(PYBINR)_$(ARCH)/$(PYBINR)
$(OPENSSL_BIN_arm): export CROSS_COMPILE="arm-linux-androideabi-"
$(OPENSSL_BIN_arm): export CC:=gcc -mtune=xscale -march=armv5te -msoft-float --sysroot=$(ANDROID_SYSROOT)
$(OPENSSL_BIN_arm): \
    export ANDROID_TOOLS="arm-linux-androideabi-gcc arm-linux-androideabi-ranlib arm-linux-androideabi-ld"

$(OPENSSL_BIN_arm): .build_armeabi/Makefile
	./showenv.sh
	cd $(dir $<); perl $(perlopt) Makefile.org
	cd $(dir $<); ./Configure $(__PIE_CFLAGS) android no-asm shared no-ssl2 no-ssl3 no-comp no-hw \
	  --openssldir=$(PREFIX)/share --prefix=$(PREFIX)
	make -C $(dir $<) depend
	make -C $(dir $<) all
	make -C $(dir $<) install_sw

# setup arch depended variables: x86
$(OPENSSL_BIN_x86): export ANDROID_API := android-9
$(OPENSSL_BIN_x86): \
    export ANDROID_TOOLCHAIN=$(NDK_PATH)/toolchains/$(eabi_x86)/prebuilt/$(host)/bin
$(OPENSSL_BIN_x86): export PATH:=$(ANDROID_TOOLCHAIN):$(PATH)
$(OPENSSL_BIN_x86): export _ANDROID_ARCH=arch-x86
$(OPENSSL_BIN_x86): export _ANDROID_EABI=$(eabi_x86)
$(OPENSSL_BIN_x86): export MACHINE=i686
$(OPENSSL_BIN_x86): export ARCH=x86
$(OPENSSL_BIN_x86): PREFIX=$(CWD)/$(PYBINR)_$(ARCH)/$(PYBINR)
$(OPENSSL_BIN_x86): export CROSS_COMPILE="i686-linux-android-"
$(OPENSSL_BIN_x86): export PATH:=$(ANDROID_TOOLCHAIN):$(PATH)
$(OPENSSL_BIN_x86): \
    export ANDROID_TOOLS="i686-linux-android-gcc arm-linux-androideabi-ranlib arm-linux-androideabi-ld"

$(OPENSSL_BIN_x86): .build_x86/Makefile
	./showenv.sh
	cd $(dir $<); perl $(perlopt) Makefile.org
	cd $(dir $<); ./config $(__PIE_CFLAGS) shared no-ssl2 no-ssl3 no-comp no-hw no-engine \
	  --openssldir=$(PREFIX)/share --prefix=$(PREFIX)
	make -C $(dir $<) depend
	make -C $(dir $<) all
	make -C $(dir $<) install_sw

.build_x86/Makefile: $(OPENSSL_SRC)
	rm -rf $(dir $@)
	tar xfz $(OPENSSL_SRC)
	mv $(OPENSSL_DIR) $(subst /,,$(dir $@))

.build_armeabi/Makefile: $(OPENSSL_SRC)
	rm -rf $(dir $@)
	tar xfz $(OPENSSL_SRC)
	mv $(OPENSSL_DIR) $(subst /,,$(dir $@))

