/*
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
import android.content.SharedPreferences;
import android.content.SharedPreferences.Editor;

import com.googlecode.android_scripting.AsyncTaskListener;
import com.googlecode.android_scripting.InterpreterUninstaller;
import com.googlecode.android_scripting.exception.Sl4aException;
import com.googlecode.android_scripting.interpreter.InterpreterDescriptor;

public class Python3Uninstaller extends InterpreterUninstaller {

  public Python3Uninstaller(InterpreterDescriptor descriptor, Context context,
      AsyncTaskListener<Boolean> listener) throws Sl4aException {
    super(descriptor, context, listener);
  }

  @Override
  protected boolean cleanup() {
    SharedPreferences storage = mContext.getSharedPreferences("python-installer", 0);
    Editor editor = storage.edit();
    editor.remove("interpreter");
    editor.remove("extras");
    editor.remove("scripts");
    editor.commit();
    /*
     * SharedPreferences def = PreferenceManager.getDefaultSharedPreferences(mContext); editor =
     * def.edit(); editor.putBoolean(InterpreterConstants.INSTALLED_PREFERENCE_KEY, false);
     * editor.commit();
     */
    return true;
  }
}
