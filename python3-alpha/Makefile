VERSION=3.4.3
ndk_build = $(NDK_PATH)/ndk-build
# set -ex
CWD := $(shell pwd)
OUT := $(CWD)/output
DEBUG=no

RELEASE_VERSION:=$(shell cat LATEST_VERSION)
PYTHONSRC := ./python-src
PYTHONNET := Python-$(VERSION).tgz
PYTHONTAR := $(CWD)/Python-$(VERSION).tgz
PYTHONLIB := python$(basename $(VERSION))
PYTHON_FOR_BUILD := $(CWD)/host/bin/python
TAR := tar xvfz
ZIP := python3_$(RELEASE_VERSION).zip \
       python3_$(RELEASE_VERSION)_x86.zip \
       python3_extras_$(shell cat LATEST_VERSION_EXTRA).zip \
       python3_scripts_$(shell cat LATEST_VERSION_SCRIPTS).zip
ZIP_PIE := python3_$(RELEASE_VERSION)_pie.zip \
           python3_$(RELEASE_VERSION)_x86_pie.zip

OUT_LIB := $(OUT)/usr/lib/$(PYTHONLIB)

.PHONY: build build_config build_bin error init clean_output cleanall \
        patch .build_misc_sqlite3_arm .build_misc_ncurses_arm \
        .build_misc_readline_arm .build_misc_bzip2_arm

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
export CFLAGS = --sysroot=$(ANDROID_NDK_SYSROOT) \
                -I$(CWD)/sqlite3 -I$(CWD)/bzip2-1.0.6 \
                -I$(CWD)
# -I$(CWD): for #include <readline/readline.h>
export LDFLAGS = --sysroot=$(ANDROID_NDK_SYSROOT) \
                 -L$(CWD)/openssl/.build_$(ARCH) \
                 -L$(CWD)/sqlite3 -L$(CWD)/bzip2-1.0.6 \
                 -L$(CWD)/readline
# CXX = ${TARGET}-g++
# AR = ${TARGET}-ar
# RANLIB=${TARGET}-ranlib
MACHINE = armv7
export ARCH = arm
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


#### libraries
sqlite3.tar.gz:
	wget -O $@ https://sqlite.org/2015/sqlite-autoconf-3080803.tar.gz
ncurses-5.9.tar.gz:
	wget http://ftp.gnu.org/pub/gnu/ncurses/ncurses-5.9.tar.gz
readline-6.3.tar.gz:
	wget ftp://ftp.gnu.org/gnu/readline/readline-6.3.tar.gz
# zlib-1.2.8.tar.gz:
# 	wget http://zlib.net/zlib-1.2.8.tar.gz
bzip-1.0.6.tar.gz:
	wget http://www.bzip.org/1.0.6/bzip2-1.0.6.tar.gz


targz = $(subst .tar.gz,,$1)

.build_misc_ncurses: ncurses-5.9.tar.gz
	tar xfz $<
	make $@_arm CROSS=arm
	touch $@
.build_misc_ncurses_arm: ncurses-5.9.tar.gz
	cd $(call targz,$<); \
	  ./configure --host=$(HOSTARCH) --target=$(HOSTARCH) --prefix=/python \
	  --enable-shared --without-cxx --without-cxx-binding
	cd $(call targz,$<); patch -p1 < android.patch
	make -C $(call targz,$<)

.build_misc_readline: readline-6.3.tar.gz
	tar xfz $<
	cd $(call targz,$<); patch < fix.patch
	make $@_arm CROSS=arm
	touch $@
.build_misc_readline_arm: readline-6.3.tar.gz
	cd $(call targz,$<); \
	   bash_cv_wcwidth_broken=no \
	   CFLAGS="$(CFLAGS) -I$(CWD)/ncurses-5.9/include" \
	   ./configure --host=$(HOSTARCH) --target=$(HOSTARCH) --prefix=/python \
	   --enable-shared --with-curses=../ncurses-5.9
	cd $(call targz,$<); patch < android.patch
	make -C $(call targz,$<)
	ln -sf $(call targz,$<) $(patsubst -6.3,,$(call targz,$<))
	touch $@

.build_misc_sqlite3: sqlite3.tar.gz
	tar xfz $<
	mv sqlite-autoconf-3080803 $(call targz,$<)
	make $@_arm CROSS=arm
	touch $@
.build_misc_sqlite3_arm: sqlite3.tar.gz
	cd $(call targz,$<); \
	   ./configure --host=$(HOSTARCH) --target=$(HOSTARCH) --prefix=/python
	make -C $(call targz,$<)

# .build_misc_zlib: zlib-1.2.8.tar.gz
# 	tar xfz $<
# 	make $@_arm CROSS=arm
# 	touch $@
# .build_misc_zlib_arm: zlib-1.2.8.tar.gz
# 	make -C $(call targz,$<)

.build_misc_bzip2: bzip2-1.0.6.tar.gz
	tar xfz $<
	cd $(call targz,$<); patch -p1 < pre.patch
	make $@_arm CROSS=arm
	touch $@
.build_misc_bzip2_arm: bzip2-1.0.6.tar.gz
	PREFIX=/python \
	  CC=$(TARGET)-gcc AR=$(TARGET)-ar RANLIB=$(TARGET)-ranlib \
	  make -C $(call targz,$<) -f Makefile-libbz2_so

.build_misc: .build_misc_sqlite3 .build_misc_ncurses \
             .build_misc_readline .build_misc_bzip2
	touch .build_misc

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

$(CWD)/Python-$(VERSION)-android.patch:
	echo
$(PYTHONSRC): $(PYTHONTAR) $(CWD)/Python-$(VERSION)-android.patch
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


.build_config: $(PYTHONSRC) .build_misc
	make build_config CROSS=arm
	touch .build_config
build_config:
	# @echo PATH: "'$$PATH'"
	@echo CFLAGS: "'$$CFLAGS'"
	cd $(PYTHONSRC); CONFIG_SITE=`pwd`/config.site \
	./configure --host=$(TARGET) --build=x86_64-linux-gnu \
	            --prefix=/python --enable-shared

.build_bin: .build_config
	make build_bin CROSS=arm
	touch .build_bin
build_bin: .build_openssl .build_misc
	make -C $(PYTHONSRC)


$(ZIP): .build_bin
	@echo non-PIE: build the android libraries/executables
	. ../VERSIONS
	ZIPMAIN=python3_r${PY34A_VERSION}.zip
	ZIPEXTRA=python3_extras_r${PY34A_EXTRAS_VERSION}.zip
	ZIPSCRIPTS=python3_scripts_r${PY34A_SCRIPTS_VERSION}.zip
	echo "Packing $ZIPMAIN"
	rm $ZIPMAIN
	pushd _install
	cp ../../thirdparty/lib/libsqlite3.so.0 python3/lib
	cp ../../thirdparty/lib/libreadline.so.6 python3/lib
	cp ../../thirdparty/lib/libncurses.so.5 python3/lib
	cp ../../thirdparty/lib/libz.so.1 python3/lib
	#Symbolic linked libs just take up space
	find python3/lib -type l -exec rm -f {} \;
	zip -g ../$ZIPMAIN python3/bin/python3
	zip -gri"*.so" -i"*.so.*" ../$ZIPMAIN python3/lib
	zip -g ../$ZIPMAIN python3/lib/python3.2/config-3.2m/Makefile python3/include/python3.2m/pyconfig.h
	popd
	
	echo "Packing $ZIPEXTRA"
	rm ${ZIPEXTRA}
	rm -rf android
	mkdir android
	mkdir android/python3
	cp android.py _install/python3/lib/python3.2
	cp -r ../extra_modules/* _install/python3/lib/python3.2
	cp -r _install/python3/lib/python3.2/* android/python3
	mkdir -p android/python3/terminfo/x
	mkdir -p android/python3/terminfo/v
	mkdir -p android/python3/terminfo/a
	cp ../thirdparty/share/terminfo/x/xterm android/python3/terminfo/x
	cp ../thirdparty/share/terminfo/a/ansi android/python3/terminfo/a
	cp ../thirdparty/share/terminfo/v/vt320 android/python3/terminfo/v
	pushd android
	zip -grx"*.so" -x"*.so.*" ../$ZIPEXTRA python3
	zip -d ../$ZIPEXTRA "*.pc" "*pkgconfig*" "*lib/libpython3.2m.a" "*/test/*" "*.a"
	popd
	pushd _install
	zip -g ../$ZIPEXTRA python3/lib/python3.2/config-3.2m/Makefile python3/lib/python3.2/site-packages/*
	popd

echo "Packing $ZIPSCRIPTS"
rm $ZIPSCRIPTS
cd android-scripts
zip -g ../$ZIPSCRIPTS *


patch:
	diff -wuprN Python-$(VERSION) $(PYTHONSRC) \
	  > Python-$(VERSION)-android.patch.new

