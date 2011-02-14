#!/bin/bash

export PY4A=`dirname $BASH_SOURCE`
export PATH="${PATH}:${ANDROID_NDK_TOOLCHAIN_ROOT}/bin"
export PY4A_INC="${PY4A}/include"
export PY4A_LIB="${PY4A}/lib"
export PYTHONPATH="${PYTHONPATH}:${PY4A}/python"
