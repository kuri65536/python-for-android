/*
 * Copyright (C) 2017, 2015 Shimoda <kuri65536@hotmail.com>
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

package com.googlecode.android_scripting.pythoncommon;

import android.content.Context;
import android.content.SharedPreferences;

import com.googlecode.android_scripting.Log;
import com.googlecode.android_scripting.interpreter.InterpreterConstants;
import com.googlecode.android_scripting.interpreter.InterpreterUtils;
import com.googlecode.android_scripting.interpreter.Sl4aHostedInterpreter;

import java.io.BufferedReader;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.InputStreamReader;
import java.net.URL;
import java.net.UnknownHostException;
import java.util.Map;

public class PythonDescriptor extends Sl4aHostedInterpreter {
    protected final String FNAME_PYEXTCFG = ".pyextpreffered";

  protected static final String PYTHON_BIN = "bin/python";
  private static final int LATEST_VERSION_FAILED = -1;
  private int cache_version = -1;
  private int cache_extras_version = -1;
  private int cache_scripts_version = -1;
  public boolean mfLocalInstall = false;
    public Boolean cachePython2Installed = null;
    public Boolean cachePython3Installed = null;
    public Integer cachedPrefferedPyExtention = null;

  // path in devices.
    protected String pathBin() {
        return "/" + PYTHON_BIN;
    }

    protected String pathEgg() {
        return this.pathShlib() + "/python2.7/egg-info";
    }

    protected String pathShlib() {
        return "/lib";
    }

    protected String pathDynload() {
        return this.pathShlib() + "/python2.7/lib-dynload";
    }

    protected String pathSitepkgs() {
        return this.pathShlib() + "/python2.7/site-packages";
    }

    // Network
    protected String urlSrc() {
        throw new UnsupportedOperationException("not implemented in sub-class.");
        // return "http://where.is.python.hosted/path/to/sources/";
    };

    protected String pathVersion() {
        return "python-build/LATEST_VERSION";
    };

    // Script settings.
  public String getExtension() {
    return ".py";
  }

  public String getName() {
    return "python";
  }

  public String getNiceName() {
    return "Python 2.7.12";
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

  protected int __resolve_version(String what) {
    // try resolving latest version
    URL url;
    try {
      url = new URL(this.urlSrc() + this.pathVersion() +
                    what.toUpperCase());
      BufferedReader reader = new BufferedReader(new InputStreamReader(url.openStream()));
      return Integer.parseInt(reader.readLine().substring(1).trim());
    } catch (UnknownHostException e) {
      Log.i("can't resolve host: " + this.urlSrc());
      return LATEST_VERSION_FAILED;
    } catch (Exception e) {
      e.printStackTrace();
      return LATEST_VERSION_FAILED;
    }
  }

  public int getVersion() {
    if (cache_version > -1) {
      return cache_version;
    }
    return getVersion(false);
  }

  public int getVersion(boolean usecache) {
    if (usecache && cache_version > -1) {
      return cache_version;
    }
    cache_version = __resolve_version("");
    return cache_version;
  }

  @Override
  public int getExtrasVersion() {
    if (cache_extras_version > -1) {
      return cache_extras_version;
    }
    return getExtrasVersion(false);
  }

  public int getExtrasVersion(boolean usecache) {
    if (usecache && cache_extras_version > -1) {
      return cache_extras_version;
    }
    cache_extras_version = __resolve_version("_extra");
    return cache_extras_version;
  }

  @Override
  public int getScriptsVersion() {
    if (cache_scripts_version > -1) {
      return cache_scripts_version;
    }
    return getScriptsVersion(false);
  }

  public int getScriptsVersion(boolean usecache) {
    if (usecache && cache_scripts_version > -1) {
      return cache_scripts_version;
    }
    cache_scripts_version = __resolve_version("_scripts");
    return cache_scripts_version;
  }

  @Override
  public File getBinary(Context context) {
    return new File(getExtrasPath(context), PYTHON_BIN);
  }

    protected File getLanguageRoot() {
        return new File(InterpreterConstants.SDCARD_ROOT,
                getClass().getPackage().getName());
    }

  protected String getExtrasRoot() {
    return getLanguageRoot().getAbsolutePath()
        + InterpreterConstants.INTERPRETER_EXTRAS_ROOT;
  }

  protected String getHome(Context context) {
    File file = InterpreterUtils.getInterpreterRoot(context, getName());
    return file.getAbsolutePath();
  }

  public String getExtras() {
    File file = new File(getExtrasRoot(), getName());
    return file.getAbsolutePath();
  }

  protected String getTemp() {
    File tmp = new File(getExtrasRoot(), getName() + "/tmp");
    if (!tmp.isDirectory()) {
      tmp.mkdir();
    }
    return tmp.getAbsolutePath();
  }

  @Override
  public Map<String, String> getEnvironmentVariables(Context context) {
        throw new UnsupportedOperationException("not implemented in sub-class.");
  }

  public void setSharedPreferences(SharedPreferences prefs) {
    cache_version = prefs.getInt(PythonConstants.AVAIL_VERSION_KEY, -1);
    cache_extras_version = prefs.getInt(PythonConstants.AVAIL_EXTRAS_KEY, -1);
    cache_scripts_version =
            prefs.getInt(PythonConstants.AVAIL_SCRIPTS_KEY, -1);
  }

  public boolean isLocalInstall() {
    return this.mfLocalInstall;
  }

    private Boolean isPythonNInstalled(int n) {
        String s = n == 2 ? "": String.format("%d", n);
        String _path = InterpreterConstants.SDCARD_ROOT +
                String.format("/com.googlecode.python%sforandroid", s) +
                InterpreterConstants.INTERPRETER_EXTRAS_ROOT;
        File path = new File(_path);
        boolean ret = path.isDirectory();
        Log.i("isPython" + n + "Installed: was cached to " + ret);
        return Boolean.valueOf(ret);
    }

    // detect Python2 is installed.
    public boolean isPython2Installed() {
        if (this.cachePython2Installed != null) {
            return this.cachePython2Installed.booleanValue();
        }
        return this.cachePython2Installed = isPythonNInstalled(2);
    }

    // detect Python3 is installed.
    public boolean isPython3Installed() {
        if (this.cachePython3Installed != null) {
            return this.cachePython3Installed.booleanValue();
        }
        return this.cachePython3Installed = isPythonNInstalled(3);
    }

    public int getPyExtPreffered() {
        if (this.cachedPrefferedPyExtention != null) {
            return this.cachedPrefferedPyExtention;
        }

        FileInputStream fp = null;
        int ret = 2;
        File fname = new File(getLanguageRoot(), FNAME_PYEXTCFG);

        if (!fname.canRead()) {
            Log.w("can't read " + fname.getName() + " fallback to " + ret);
            return ret;
        } else try {
            fp = new FileInputStream(fname);
            ret = fp.read() - '0';
        } catch (IOException ex) {
            Log.w("can't read " + fname.getName() + " fallback to " +
                  ret + " by exception: " + ex.toString());
            return ret;
        }
        this.cachedPrefferedPyExtention = ret;
        return ret;
    }

    public int putPyExtPreffered(int n) {
        FileOutputStream fp = null;

        int m = getPyExtPreffered();
        File fname = new File(getLanguageRoot(), FNAME_PYEXTCFG);
        if (fname.exists() && !fname.canWrite()) {
            Log.w("can't write " + n + " to: " + fname.getAbsolutePath());
            return m;
        } else try {
            fp = new FileOutputStream(fname);
            fp.write('0' + n);
        } catch (IOException ex) {
            Log.w("can't write " + n + " to: " + fname.getName() +
                  " with exception:" + ex.toString());
            return m;
        }
        this.cachedPrefferedPyExtention = null;
        return n;
    }
}
