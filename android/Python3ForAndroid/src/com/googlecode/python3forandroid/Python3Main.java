/*
 * Copyright (C) 2015 Shimoda
 * Copyright (C) 2010-2011 Naranjo Manuel Francisco <manuel@aircable.net>
 * Copyright (C) 2010-2011 Robbie Matthews <rjmatthews62@gmail.com>
 * Copyright (C) 2009 Google Inc.
 *
 * Licensed under the Apache License, Version 2.0 (the "License"); you may not
 * use this file except in compliance with the License. You may obtain a copy of
 * the License at
 *
 * http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
 * WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
 * License for the specific language governing permissions and limitations under
 * the License.
 */

package com.googlecode.python3forandroid;

import android.content.Context;

import com.googlecode.android_scripting.AsyncTaskListener;
import com.googlecode.android_scripting.InterpreterInstaller;
import com.googlecode.android_scripting.InterpreterUninstaller;
import com.googlecode.android_scripting.exception.Sl4aException;
import com.googlecode.android_scripting.interpreter.InterpreterDescriptor;
import com.googlecode.android_scripting.pythoncommon.PythonMain;

/**
 * Python Installer. Incorporates module installer.
 * 
 * The module installer reads a zip file previously downloaded into "download", and unpacks it. If
 * the module contains shared libraries (*.so) then the module is unpacked into data, other installs
 * in extras.
 * 
 * Typically, these will be /data/data/com.googlecode.python3forandroid/files/python/lib/python3.6
 * and /sdcard/com.googlecode.pythonforandroid/extras respectively.
 * 
 * Egg files are just copied into
 * /data/data/com.googlecode.python3forandroid/files/python/lib/python3.6
 * 
 * @author Damon
 * @author Robbie Matthews (rjmatthews62@gmail.com)
 * @author Manuel Naranjo (manuel@aircable.net)
 */

// TODO:(Robbie) The whole Import Module is more of a proof of concept than a fully realised
// process. Needs some means of checking that these are properly formatted zip files, and probably a
// means of uninstalling as well. Import handling could well be a separate activity, too.
public class Python3Main extends PythonMain {

    @Override
    public String getPfxPython() {
        return "python3";
    }

  @Override
  protected InterpreterDescriptor getDescriptor() {
    mDescriptor = new Python3Descriptor();
    return mDescriptor;
  }

  @Override
  protected InterpreterInstaller getInterpreterInstaller(InterpreterDescriptor descriptor,
      Context context, AsyncTaskListener<Boolean> listener) throws Sl4aException {
    return new Python3Installer(descriptor, context, listener);
  }

  @Override
  protected InterpreterUninstaller getInterpreterUninstaller(InterpreterDescriptor descriptor,
      Context context, AsyncTaskListener<Boolean> listener) throws Sl4aException {
    return new Python3Uninstaller(descriptor, context, listener);
  }
}
