/*
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
import android.content.SharedPreferences;
import android.os.Environment;

import com.googlecode.android_scripting.FileUtils;
import com.googlecode.android_scripting.Log;
import com.googlecode.android_scripting.interpreter.InterpreterConstants;
import com.googlecode.android_scripting.interpreter.Sl4aHostedInterpreter;

import java.io.File;
import java.util.HashMap;
import java.util.Map;

public class Python3Descriptor extends Sl4aHostedInterpreter {

  private static final String PYTHON_BIN = "python3/bin/python3";
  private static final String ENV_HOME = "PYTHONHOME";
  private static final String ENV_PATH = "PYTHONPATH";
  private static final String ENV_TEMP = "TEMP";
  private static final String ENV_LD = "LD_LIBRARY_PATH";
  private static final String ENV_EXTRAS = "PY4A_EXTRAS";
  private static final String ENV_EGGS = "PYTHON_EGG_CACHE";
  private static final String ENV_USERBASE = "PYTHONUSERBASE";
  // static final String BASE_URL = "http://python-for-android.googlecode.com/files";
  static final String BASE_URL = "http://www.mithril.com.au/android";
  private static final int LATEST_VERSION = 5;
  private int cache_scripts_version = -1;
  private SharedPreferences mPreferences;

  @Override
  public int getVersion() {
    if (mPreferences != null) {
      return mPreferences.getInt(Python3Constants.AVAIL_VERSION_KEY, LATEST_VERSION);
    } else {
      return LATEST_VERSION;
    }
  }

  @Override
  public int getExtrasVersion() {
    if (mPreferences != null) {
      return mPreferences.getInt(Python3Constants.AVAIL_EXTRAS_KEY, LATEST_VERSION);
    } else {
      return super.getExtrasVersion();
    }
  }

  @Override
  public String getBaseInstallUrl() {
    return BASE_URL + "/";
  }

  public String getExtension() {
    return ".py";
  }

  public String getName() {
    return "python3";
  }

  public String getNiceName() {
    return "Python 3.2.2";
  }

  public boolean hasInterpreterArchive() {
    return true;
  }

  public boolean hasExtrasArchive() {
    return true;
  }

  public boolean hasScriptsArchive() {
    return true;
  }

  @Override
  public int getScriptsVersion() {
    if (mPreferences != null) {
      return mPreferences.getInt(Python3Constants.AVAIL_SCRIPTS_KEY, LATEST_VERSION);
    }
    return super.getScriptsVersion();
  }

  public int getScriptsVersion(boolean usecache) {
    if (usecache && cache_scripts_version > -1) {
      return cache_scripts_version;
    }
    return getScriptsVersion();
  }

  @Override
  public File getBinary(Context context) {
    File f = new File(context.getFilesDir(), PYTHON_BIN);
    return f;
    // return new File(getExtrasPath(context), PYTHON_BIN);
  }

  private String getExtrasRoot() {
    return InterpreterConstants.SDCARD_ROOT + getClass().getPackage().getName()
        + InterpreterConstants.INTERPRETER_EXTRAS_ROOT;
  }

  private String getHome(Context context) {
    return context.getFilesDir().getAbsolutePath();
    // File file = InterpreterUtils.getInterpreterRoot(context, "");
    // return file.getAbsolutePath();
  }

  public String getExtras() {
    File file = new File(getExtrasRoot(), getName());
    return file.getAbsolutePath();
  }

  private String getTemp() {
    File tmp = new File(getExtrasRoot(), "/tmp");
    if (!tmp.isDirectory()) {
      tmp.mkdir();
    }
    return tmp.getAbsolutePath();
  }

  @Override
  public Map<String, String> getEnvironmentVariables(Context context) {
    Map<String, String> values = new HashMap<String, String>();
    String home = getHome(context);
    String libs = new File(getExtrasRoot(), "python3").getAbsolutePath();
    values.put(ENV_HOME, libs + ":" + new File(home, "python3").getAbsolutePath());
    values.put(ENV_LD, new File(home, "python3/lib").getAbsolutePath());
    values.put(ENV_PATH, new File(home, "python3/lib/python3.2") + ":"
        + new File(home, "python3/lib/python3.2/lib-dynload") + ":" + libs);
    values.put(ENV_EGGS,
        new File(getHome(context), "python3/lib/python3.2/lib-dynload").getAbsolutePath());
    values.put(ENV_EXTRAS, getExtrasRoot());
    values.put(ENV_USERBASE, home);
    String temp = context.getCacheDir().getAbsolutePath();
    values.put(ENV_TEMP, temp);
    try {
      FileUtils.chmod(context.getCacheDir(), 0777); // Make sure this is writable.
    } catch (Exception e) {
    }
    values.put("HOME", Environment.getExternalStorageDirectory().getAbsolutePath());
    for (String k : values.keySet()) {
      Log.d(k + " : " + values.get(k));
    }
    return values;
  }

  void setSharedPreferences(SharedPreferences preferences) {
    mPreferences = preferences;
  }
}
