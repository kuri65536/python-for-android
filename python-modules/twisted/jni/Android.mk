# Copyright (C) 2009 The Android Open Source Project
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
#
LOCAL_PATH := $(call my-dir)
PYTHONLIB := $(LOCAL_PATH)/../../python-lib

# _epoll.so
include $(CLEAR_VARS)
LOCAL_C_INCLUDES := $(PYTHONLIB)/include/python2.6
LOCAL_MODULE    := epoll
LOCAL_MODULE_FILENAME := _epoll
LOCAL_LDLIBS := -L$(PYTHONLIB)/lib/ -lpython2.6
LOCAL_SRC_FILES := python/_epoll.c
include $(BUILD_SHARED_LIBRARY)

# _initgroups.so
include $(CLEAR_VARS)
LOCAL_C_INCLUDES := $(PYTHONLIB)/include/python2.6
LOCAL_MODULE    := initgroups
LOCAL_MODULE_FILENAME := _initgroups
LOCAL_LDLIBS := -L$(PYTHONLIB)/lib/ -lpython2.6
LOCAL_SRC_FILES := python/_initgroups.c
include $(BUILD_SHARED_LIBRARY)

# _sigchld.so
include $(CLEAR_VARS)
LOCAL_C_INCLUDES := $(PYTHONLIB)/include/python2.6
LOCAL_MODULE    := sigchld
LOCAL_MODULE_FILENAME := _sigchld
LOCAL_LDLIBS := -L$(PYTHONLIB)/lib/ -lpython2.6
LOCAL_SRC_FILES := internet/_sigchld.c
include $(BUILD_SHARED_LIBRARY)

# _c_urlarg.so
include $(CLEAR_VARS)
LOCAL_C_INCLUDES := $(PYTHONLIB)/include/python2.6
LOCAL_MODULE    := _c_urlarg
LOCAL_MODULE_FILENAME := _c_urlarg
LOCAL_LDLIBS := -L$(PYTHONLIB)/lib/ -lpython2.6
LOCAL_SRC_FILES := protocols/_c_urlarg.c
include $(BUILD_SHARED_LIBRARY)

# raiser.so
include $(CLEAR_VARS)
LOCAL_C_INCLUDES := $(PYTHONLIB)/include/python2.6
LOCAL_MODULE    := raiser
LOCAL_MODULE_FILENAME := raiser
LOCAL_LDLIBS := -L$(PYTHONLIB)/lib/ -lpython2.6
LOCAL_SRC_FILES := test/raiser.c
include $(BUILD_SHARED_LIBRARY)
