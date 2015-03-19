VERSION=2.7.8
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

OUT_LIB := $(OUT)/usr/lib/$(PYTHONLIB)

.PHONY: build error init

ifeq (x$(NDK_PATH),x)
build: error
else
build: $(PYTOHNTAR) .build_host $(PYTHONSRC) .build_android
endif

init:
	rm -f $(PYTHONTAR) .build_host $(PYTHONSRC) .build_android

error:
	@echo please set NDK_PATH to android-ndk-r10d or later::
	@echo "  $$ NDK_PATH=/path/to/android-ndk-r10d make build"


$(PYTHONTAR):
	echo "Building Python VM For Android Release $(RELEASE_VERSION)"
	rm -rf python*$(RELEASE_VERSION).zip
	if [ ! -f $(CWD)/Python-$(VERSION).tar.bz2 ]; then \
	    URL="http://www.python.org/ftp/python/$(VERSION)/$(PYTHONNET)"; \
	    wget -O $(PYTHONTAR) $$URL; \
	fi

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

$(PYTHONSRC): $(PYTHONTAR)
	$(TAR) $(PYTHONTAR)
	mv Python-$(VERSION) $(PYTHONSRC)
	cd $(PYTHONSRC); \
	patch -p1 -i $(CWD)/Python-$(VERSION)-android.patch

LIBS = site-packages encodings compiler hotshot \
    email email/mime \
    json \
    sqlite3 \
    logging bsddb csv wsgiref \
    ctypes ctypes/macholib idlelib idlelib/Icons \
    distutils distutils/command \
    multiprocessing multiprocessing/dummy \
    lib-old \
    plat-linux2 \
    xml xml/dom xml/etree xml/parsers xml/sax \


.build_android: $(PYTHONSRC)
	rm -rf $(OUT)*
	mkdir -p $(OUT)/usr/bin
	mkdir -p $(OUT)/usr/lib/$(PYTHONLIB)/lib-dynload
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
	
	# build the android needed libraries
	cd $(CWD)/python; \
	$(CWD)/host/pgen $(CWD)/python-src/Grammar/Grammar \
	    $(CWD)/python-src/Include/graminit.h \
	    $(CWD)/python-src/Python/graminit.c
	cd $(CWD)/python; NDK_MODULE_PATH=$(shell pwd) $(ndk_build)
	
	# copy out all the needed files
	cd $(CWD)/python; \
	mv obj/local/armeabi/python $(OUT)/usr/bin; \
	mv obj/local/armeabi/lib*.so $(OUT)/usr/lib; \
	mv obj/local/armeabi/*.so $(OUT)/usr/lib/$(PYTHONLIB)/lib-dynload; \
	
	cd $(CWD)/python-libs; bash -ex setuptools.sh
	$(CWD)/host/bin/python $(OUT)/usr/lib/$(PYTHONLIB)/compileall.py $(OUT)/usr/lib/$(PYTHONLIB)
	$(CWD)/host/bin/python build.py
	
	echo "Done"
	touch .build_android

