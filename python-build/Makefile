VERSION=2.7.9
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
PYTHONHST := $(CWD)/host
TAR := tar xvfz
ZIP := python_$(RELEASE_VERSION).zip \
       python_$(RELEASE_VERSION)_x86.zip \
       python_extras_$(shell cat LATEST_VERSION_EXTRA).zip \
       python_scripts_$(shell cat LATEST_VERSION_SCRIPTS).zip
ZIP_PIE := python_$(RELEASE_VERSION)_pie.zip \
           python_$(RELEASE_VERSION)_x86_pie.zip

OUT_LIB := $(OUT)/usr/lib/$(PYTHONLIB)

.PHONY: build error init clean_output cleanall

ifeq (x$(NDK_PATH),x)
build: error
else
build: $(ZIP) $(ZIP_PIE)
endif

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

.build_host: $(PYTHONTAR)
	# we need to build the host python and host pgen so we can
	# generate the correct grammar and some other stuff
	echo "Decompressing Python-$(VERSION)"
	$(TAR) $(PYTHONTAR)
	mkdir -p $(PYTHONHST)
	cd Python-$(VERSION)/; ./configure --prefix=$(PYTHONHST)
	make -C Python-$(VERSION)
	make -C Python-$(VERSION) install
	cp Python-$(VERSION)/Parser/pgen $(PYTHONHST)
	rm -rf Python-$(VERSION)
	touch .build_host

$(PYTHONSRC): $(PYTHONTAR) .build_host
	$(TAR) $(PYTHONTAR)
	mv Python-$(VERSION) $(PYTHONSRC)
	cd $(PYTHONSRC); \
	patch -p1 -i $(CWD)/Python-$(VERSION)-android.patch

LIBS = site-packages encodings compiler hotshot \
    email email/mime \
    json \
    sqlite3 \
    logging bsddb wsgiref \
    ctypes ctypes/macholib idlelib idlelib/Icons \
    distutils distutils/command \
    multiprocessing multiprocessing/dummy \
    plat-linux2 \
    xml xml/dom xml/etree xml/parsers xml/sax \

# libraries {{{1
TARGET_LIBS := .build_misc_sqlite3 \
               .build_misc_bzip2
targz = $(subst .tar.gz,,$1)

## download {{{2
sqlite3.tar.gz:
	wget -O $@ http://sqlite.org/2015/sqlite-autoconf-3080900.tar.gz
bzip2-1.0.6.tar.gz:
	wget http://www.bzip.org/1.0.6/bzip2-1.0.6.tar.gz

## sqlite3 {{{2
.build_misc_sqlite3: sqlite3.tar.gz
	rm -rf $(call targz,$<)
	tar xfz $<
	mv sqlite-autoconf-3080900 $(call targz,$<)
	cp sqlite3.mk $(call targz,$<)/Android.mk
	touch $@
.build_misc_bzip2: bzip2-1.0.6.tar.gz
	rm -rf bzip2
	tar xfz $<
	cd $(call targz,$<); patch -p1 < $(CWD)/../python3-alpha/patches/bzip2-1.0.6-pre.patch
	mv $(call targz,$<) bzip2
	cp bzip2.mk bzip2/Android.mk
	touch $@

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
	
	cd $(PYTHONSRC); $(PYTHONHST)/bin/python Lib/sysconfig.py --generate-posix-vars
	cp $(PYTHONSRC)/build/lib*/_sysconfigdata.py $(OUT_LIB)/
	cp $$(find $(PYTHONSRC)/Lib/ -maxdepth 1 -type f) $(OUT_LIB)/
	cp -r $(PYTHONSRC)/Include/* $(OUT)/usr/include/$(PYTHONLIB)/
	cp $(PYTHONSRC)/pyconfig.h $(OUT)/usr/include/$(PYTHONLIB)/


$(ZIP): $(PYTHONSRC) .build_openssl $(TARGET_LIBS)
	@echo non-PIE: build the android libraries/executables
	mkdir -p ./python/obj/local/{armeabi,x86}
	cp -dp openssl/.build_armeabi/lib*.so ./python/obj/local/armeabi
	cp -dp openssl/.build_x86/lib*.so ./python/obj/local/x86
	
	cd $(CWD)/python; \
	$(CWD)/host/pgen $(CWD)/python-src/Grammar/Grammar \
	    $(CWD)/python-src/Include/graminit.h \
	    $(CWD)/python-src/Python/graminit.c
	cd $(CWD)/python; NDK_MODULE_PATH=$(shell pwd) $(ndk_build)
	cd $(CWD)/python; NDK_MODULE_PATH=$(shell pwd) $(ndk_build) APP_ABI:=x86
	touch .build_bin
	
	# arm: copy out all the needed files
	make clean_output
	cd $(CWD)/python; \
	cp obj/local/armeabi/python $(OUT)/usr/bin; \
	cp -dp obj/local/armeabi/lib*.so* $(OUT)/usr/lib; \
	cp obj/local/armeabi/*.so $(OUT)/usr/lib/$(PYTHONLIB)/lib-dynload; \
	
	cd $(CWD)/python-libs; bash -ex setuptools.sh
	$(CWD)/host/bin/python $(OUT)/usr/lib/$(PYTHONLIB)/compileall.py $(OUT)/usr/lib/$(PYTHONLIB)
	$(CWD)/host/bin/python build.py
	
	# x86: copy out all the needed files
	make clean_output
	cd $(CWD)/python; \
	cp obj/local/x86/python $(OUT)/usr/bin; \
	cp -dp obj/local/x86/lib*.so* $(OUT)/usr/lib; \
	cp obj/local/x86/*.so $(OUT)/usr/lib/$(PYTHONLIB)/lib-dynload
	$(CWD)/host/bin/python build.py x86
	
	echo "Done"

$(ZIP_PIE): $(PYTHONSRC) .build_openssl $(TARGET_LIBS)
	@echo PIE: build the android libraries/executables
	mkdir -p ./python/obj/local/{armeabi,x86}
	cp -dp openssl/.build_armeabi/lib*.so* ./python/obj/local/armeabi
	cp -dp openssl/.build_x86/lib*.so* ./python/obj/local/x86
	
	# FIXME: do not build duplicated bins with non-PIE binary.
	cd $(CWD)/python; \
	$(CWD)/host/pgen $(CWD)/python-src/Grammar/Grammar \
	    $(CWD)/python-src/Include/graminit.h \
	    $(CWD)/python-src/Python/graminit.c
	cd $(CWD)/python; __ENABLE_PIE=yes NDK_MODULE_PATH=$(shell pwd) $(ndk_build)
	cd $(CWD)/python; __ENABLE_PIE=yes NDK_MODULE_PATH=$(shell pwd) $(ndk_build) APP_ABI:=x86
	touch .build_bin_pie
	
	# arm: copy out all the needed files
	make clean_output
	cd $(CWD)/python; \
	cp obj/local/armeabi/python $(OUT)/usr/bin; \
	cp -dp obj/local/armeabi/lib*.so* $(OUT)/usr/lib; \
	cp obj/local/armeabi/*.so $(OUT)/usr/lib/$(PYTHONLIB)/lib-dynload
	$(CWD)/host/bin/python build.py pie
	
	# x86: copy out all the needed files
	make clean_output
	cd $(CWD)/python; \
	cp obj/local/x86/python $(OUT)/usr/bin; \
	cp -dp obj/local/x86/lib*.so* $(OUT)/usr/lib; \
	cp obj/local/x86/*.so $(OUT)/usr/lib/$(PYTHONLIB)/lib-dynload
	$(CWD)/host/bin/python build.py pie x86
	
	echo "Done"

