VERSION=3.4.3
ndk_build = $(NDK_PATH)/ndk-build
# set -ex
CWD := $(shell pwd)
OUT := $(CWD)/output
DEBUG=no

RELEASE_VERSION:=$(shell cat LATEST_VERSION)
PYTHONSRC := $(CWD)/python-src
PYTHONNET := Python-$(VERSION).tgz
PYTHONTAR := $(CWD)/Python-$(VERSION).tgz
PYTHONLIB := python$(basename $(VERSION))
PYTHON_FOR_BUILD := $(CWD)/host/bin/python
TAR := tar xvfz
ZIP := python_$(RELEASE_VERSION).zip \
       python_$(RELEASE_VERSION)_x86.zip \
       python_extras_$(shell cat LATEST_VERSION_EXTRA).zip \
       python_scripts_$(shell cat LATEST_VERSION_SCRIPTS).zip
ZIP_PIE := python_$(RELEASE_VERSION)_pie.zip \
           python_$(RELEASE_VERSION)_x86_pie.zip

OUT_LIB := $(OUT)/usr/lib/$(PYTHONLIB)

.PHONY: build build_config build_bin error init clean_output cleanall patch

ifeq (x$(NDK_PATH),x)
build: error
else
build: $(ZIP) $(ZIP_PIE)
endif

ifeq (x$(host),x)
# check host variable: linux-x86_64, linux-x86 or darwin-x86
host = $(shell uname -s | tr A-Z a-z)-$(shell uname -m)
endif

# build variables for cross-compile.
ifeq (x$(CROSS),xarm)
TARGET := arm-linux-androideabi
tabi := $(TARGET)-4.9
# ANDROID_API := android-4     # TODO: missing waitid
ANDROID_API := android-9
ANDROID_TOOLCHAIN := $(NDK_PATH)/toolchains/$(tabi)/prebuilt/$(host)/bin
export PATH := $(ANDROID_TOOLCHAIN):$(PATH)
_ANDROID_ARCH = arch-arm
_ANDROID_EABI = $(tabi)
export CFLAGS = --sysroot=$(ANDROID_NDK_SYSROOT)
export LDFLAGS = --sysroot=$(ANDROID_NDK_SYSROOT)
# CXX = ${TARGET}-g++
# AR = ${TARGET}-ar
# RANLIB=${TARGET}-ranlib
MACHINE = armv7
ARCH = arm
HOSTPGEN = $(PYTHONSRC)/Parser/hostpgen
BLDSHARED = arm-linux-androideabi-gcc -shared
CROSS_COMPILE = arm-linux-androideabi-
CROSS_COMPILE_TARGET = arm
HOSTARCH = arm-linux-androideabi
BUILDARCH = x86_64-linux-gnu
endif

ANDROID_NDK_ROOT := $(NDK_PATH)
ANDROID_SYSROOT = $(NDK_PATH)/platforms/$(ANDROID_API)/$(_ANDROID_ARCH)
SYSROOT = $(ANDROID_SYSROOT)
NDK_SYSROOT = $(ANDROID_SYSROOT)
ANDROID_NDK_SYSROOT = $(ANDROID_SYSROOT)
ANDROID_DEV = $(ANDROID_SYSROOT)/usr


cleanall: clean
	rm -f $(PYTHONTAR)

clean: clean_output
	make -C openssl clean
	rm -f .build_*
	rm -rf $(PYTHONSRC)

error:
	@echo please set NDK_PATH to android-ndk-r10d or later::
	@echo "  $$ NDK_PATH=/path/to/android-ndk-r10d make build"


$(PYTHONTAR):
	@echo "Building Python VM For Android Release $(RELEASE_VERSION)"
	if [ ! -f $(CWD)/Python-$(VERSION).tar.bz2 ]; then \
	    URL="http://www.python.org/ftp/python/$(VERSION)/$(PYTHONNET)"; \
	    wget -O $(PYTHONTAR) $$URL; \
	fi

.build_openssl: $(PYTHONTAR)
	make -C openssl build
	touch .build_openssl

.build_host: HOSTPYTHON:=$(dir $(dir PYTHON_FOR_BUILD))
.build_host: $(PYTHONTAR)
	# we need to build the host python and host pgen so we can
	# generate the correct grammar and some other stuff
	echo "Decompressing Python-$(VERSION)"
	$(TAR) $(PYTHONTAR)
	mkdir -p $(HOSTPYTHON)
	cd Python-$(VERSION)/; ./configure --prefix=$(HOSTPYTHON)
	make -C Python-$(VERSION)
	make -C Python-$(VERSION) install
	cp Python-$(VERSION)/Parser/pgen $(HOSTPYTHON)
	rm -rf Python-$(VERSION)
	touch .build_host

$(PYTHONSRC): $(PYTHONTAR)
	rm -rf $(PYTHONSRC)
	$(TAR) $(PYTHONTAR)
	mv Python-$(VERSION) $(PYTHONSRC)
	cd $(PYTHONSRC); \
	patch -p1 -i $(CWD)/Python-$(VERSION)-android.patch


clean_output:
	rm -rf $(OUT)*
	mkdir -p $(OUT)/usr/bin
	mkdir -p $(OUT_LIB)/lib-dynload
	mkdir -p $(OUT)/usr/include/$(PYTHONLIB)
	
	for lib in $(LIBS); do \
	    if [ -n "$$(find $(PYTHONSRC)/Lib/$$lib -maxdepth 1 -type f)" ]; then \
	        mkdir -p $(OUT_LIB)/$$lib; \
	        cp $$(find $(PYTHONSRC)/Lib/$$lib -maxdepth 1 -type f) \
	           $(OUT_LIB)/$$lib; \
	    fi; \
	done
	
	cd $(PYTHONSRC); $(PYTHON_FOR_BUILD) Lib/sysconfig.py --generate-posix-vars
	cp $(PYTHONSRC)/build/lib*/_sysconfigdata.py $(OUT_LIB)/
	cp $$(find $(PYTHONSRC)/Lib/ -maxdepth 1 -type f) $(OUT_LIB)/
	cp -r $(PYTHONSRC)/Include/* $(OUT)/usr/include/$(PYTHONLIB)/
	cp $(PYTHONSRC)/pyconfig.h $(OUT)/usr/include/$(PYTHONLIB)/


.build_config: $(PYTHONSRC)
	make build_config CROSS=arm
	touch .build_config

build_config:
	# @echo PATH: "'$$PATH'"
	@echo CFLAGS: "'$$CFLAGS'"
	cd $(PYTHONSRC); CONFIG_SITE=`pwd`/config.site \
	./configure --host=$(TARGET) --build=x86_64-linux-gnu \
	            --prefix=/python --enable-shared
build_bin:
	make -C $(PYTHONSRC)
	touch .build_config

.build_bin: .build_config
	make build_bin CROSS=arm
	touch .build_bin


$(ZIP): .build_bin .build_openssl
	@echo non-PIE: build the android libraries/executables
	cp openssl/.build_arm/lib*.so ./python/obj/local/armeabi
	cp openssl/.build_x86/lib*.so ./python/obj/local/x86
	
	cd python; NDK_MODULE_PATH=$(shell pwd) $(ndk_build)
	cd python; NDK_MODULE_PATH=$(shell pwd) $(ndk_build) APP_ABI=x86
	
	# arm: copy out all the needed files
	make clean_output
	cd $(CWD)/python; \
	cp obj/local/armeabi/python $(OUT)/usr/bin; \
	cp obj/local/armeabi/lib*.so $(OUT)/usr/lib; \
	cp obj/local/armeabi/*.so $(OUT)/usr/lib/$(PYTHONLIB)/lib-dynload; \
	
	cd $(CWD)/python-libs; bash -ex setuptools.sh
	$(CWD)/host/bin/python $(OUT)/usr/lib/$(PYTHONLIB)/compileall.py $(OUT)/usr/lib/$(PYTHONLIB)
	$(CWD)/host/bin/python build.py
	
	# x86: copy out all the needed files
	make clean_output
	cd $(CWD)/python; \
	cp obj/local/x86/python $(OUT)/usr/bin; \
	cp obj/local/x86/lib*.so $(OUT)/usr/lib; \
	cp obj/local/x86/*.so $(OUT)/usr/lib/$(PYTHONLIB)/lib-dynload
	$(CWD)/host/bin/python build.py x86
	
	echo "Done"

$(ZIP_PIE): $(PYTHONSRC) .build_openssl
	@echo PIE: build the android libraries/executables
	cp openssl/.build_arm/lib*.so ./python/obj/local/armeabi
	cp openssl/.build_x86/lib*.so ./python/obj/local/x86
	
	# FIXME: do not build duplicated bins with non-PIE binary.
	cd $(CWD)/python; \
	$(CWD)/host/pgen $(CWD)/python-src/Grammar/Grammar \
	    $(CWD)/python-src/Include/graminit.h \
	    $(CWD)/python-src/Python/graminit.c
	cd $(CWD)/python; __ENABLE_PIE=yes NDK_MODULE_PATH=$(shell pwd) $(ndk_build)
	cd $(CWD)/python; __ENABLE_PIE=yes NDK_MODULE_PATH=$(shell pwd) $(ndk_build) APP_ABI:=x86
	
	# arm: copy out all the needed files
	make clean_output
	cd $(CWD)/python; \
	mv obj/local/armeabi/python $(OUT)/usr/bin; \
	mv obj/local/armeabi/lib*.so $(OUT)/usr/lib; \
	mv obj/local/armeabi/*.so $(OUT)/usr/lib/$(PYTHONLIB)/lib-dynload
	$(CWD)/host/bin/python build.py pie
	
	# x86: copy out all the needed files
	make clean_output
	cd $(CWD)/python; \
	mv obj/local/x86/python $(OUT)/usr/bin; \
	mv obj/local/x86/lib*.so $(OUT)/usr/lib; \
	mv obj/local/x86/*.so $(OUT)/usr/lib/$(PYTHONLIB)/lib-dynload
	$(CWD)/host/bin/python build.py pie x86
	
	echo "Done"

patch:
	diff -wuprN Python-$(VERSION) $(PYTHONSRC) \
	  > Python-$(VERSION)-android.patch.new

