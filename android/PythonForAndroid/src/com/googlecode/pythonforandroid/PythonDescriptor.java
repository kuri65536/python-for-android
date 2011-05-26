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

package com.googlecode.pythonforandroid;

import android.content.Context;

import com.googlecode.android_scripting.interpreter.InterpreterConstants;
import com.googlecode.android_scripting.interpreter.Sl4aHostedInterpreter;

import java.io.BufferedReader;
import java.io.File;
import java.io.InputStreamReader;
import java.net.URL;
import java.util.HashMap;
import java.util.Map;

public class PythonDescriptor extends Sl4aHostedInterpreter {

  private static final String PYTHON_BIN = "bin/python";
  private static final String ENV_HOME = "PYTHONHOME";
  private static final String ENV_PATH = "PYTHONPATH";
  private static final String ENV_TEMP = "TEMP";
  private static final String ENV_LD = "LD_LIBRARY_PATH";
  private static final String ENV_EXTRAS = "PY4A_EXTRAS";
  private static final String ENV_EGGS = "PYTHON_EGG_CACHE";
  private static final String ENV_USERBASE="PYTHONUSERBASE";
  private static final String BASE_URL = "http://python-for-android.googlecode.com/";
  private static final int LATEST_VERSION = -1;
  private int cache_scripts_version = -1;

  @Override
  public int getVersion() {
    return 16;
  }

  @Override
  public String getBaseInstallUrl() {
    return BASE_URL + "/files/";
  }

  public String getExtension() {
    return ".py";
  }

  public String getName() {
    return "python";
  }

  public String getNiceName() {
    return "Python 2.6.2";
  }

  public boolean hasInterpreterArchive() {
    return false;
  }

  public boolean hasExtrasArchive() {
    return false;
  }

  public boolean hasScriptsArchive() {
    return true;
  }

  private int __resolve_version(String what) {
    // try resolving latest version from server
    URL url;
    try {
      url = new URL(BASE_URL + "hg/python-build/LATEST_VERSION" + what.toUpperCase());
      BufferedReader reader = new BufferedReader(new InputStreamReader(url.openStream()));
      return Integer.parseInt(reader.readLine().substring(1).trim());
    } catch (Exception e) {
      // TODO Auto-generated catch block
      e.printStackTrace();

    }
    return LATEST_VERSION;
  }

  @Override
  public int getScriptsVersion() {
    cache_scripts_version = __resolve_version("_scripts");
    return cache_scripts_version;
  }

  public int getScriptsVersion(boolean usecache) {
    if (usecache && cache_scripts_version > -1) {
      return cache_scripts_version;
    }
    return getScriptsVersion();
  }

  @Override
  public File getBinary(Context context) {
    return new File(context.getFilesDir(), PYTHON_BIN);
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
    File tmp = new File(getExtrasRoot(), getName() + "/tmp");
    if (!tmp.isDirectory()) {
      tmp.mkdir();
    }
    return tmp.getAbsolutePath();
  }

  @Override
  public Map<String, String> getEnvironmentVariables(Context context) {
    Map<String, String> values = new HashMap<String, String>();
    values.put(ENV_HOME, getHome(context));
    values.put(ENV_LD, new File(getHome(context), "lib").getAbsolutePath());
    values.put(ENV_PATH, new File(getHome(context), "lib/python2.6/python.zip/python") + ":"
        + new File(getHome(context), "lib/python2.6/lib-dynload"));
    values.put(ENV_EGGS, new File(getHome(context), "lib/python2.6/lib-dynload").getAbsolutePath());
    values.put(ENV_EXTRAS, getExtrasRoot());
    values.put(ENV_USERBASE, getHome(context));
    values.put(ENV_TEMP, getTemp());
    return values;
  }
}
