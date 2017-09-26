/*
 * Copyright (C) 2017, 2015 Shimoda <kuri65536@hotmail.com>
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
import android.os.Environment;

import com.googlecode.android_scripting.Exec;
import com.googlecode.android_scripting.FileUtils;
import com.googlecode.android_scripting.Log;
import com.googlecode.android_scripting.pythoncommon.PythonConstants;
import com.googlecode.android_scripting.pythoncommon.PythonDescriptor;

import java.io.BufferedReader;
import java.io.File;
import java.io.FileDescriptor;
import java.io.FileInputStream;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.OutputStream;
import java.util.HashMap;
import java.util.Map;

public class Python3Descriptor extends PythonDescriptor {
    private static String[] PYVER = {"3", "6", "2"};
    private String[] PYVERcached = null;

  private static final String PYTHON_BIN = "python3/bin/python3";

    private String[] getVersionSeq(Context ctx) {
        if (PYVERcached != null) {return PYVERcached;}

        // fallback, recent version.
        int code;
        int[] pid = new int[1];
        Process prc;
        String path;
        File bin, lib;

        if (ctx != null) {
            path = ctx.getFilesDir().getAbsolutePath();
        } else {
            path = Environment.getDataDirectory().getAbsolutePath() +
                    "/data/com.googlecode.python3forandroid/files";
        }
        bin = new File(path, PYTHON_BIN);
        lib = new File(path, "python3/lib");

        try {
            String[] cmds = {bin.getAbsolutePath(), "-V"};
            String[] envs = {"LD_LIBRARY_PATH=" + lib.getAbsolutePath()};
            prc = Runtime.getRuntime().exec(cmds, envs);
        } catch (Exception ex) {
            Log.e("run '" + bin.getAbsolutePath() +
                    " -V' failed, fallback to default...");
            return PYVERcached = PYVER;
        }

        String s = null;
        try {
            BufferedReader reader = new BufferedReader(
                    new InputStreamReader(prc.getInputStream()));
            while ((s = reader.readLine()) != null) {
                break;
            }
            reader.close();
        } catch (IOException e) {
            Log.e("'" + pathBin() + " -V' failed...");
            s = null;
        }
        if (s == null) {
            Log.e("can't receive cmd output, fallback to default...");
            return PYVERcached = PYVER;
        }
        if (s.startsWith("Python ")) {
            s = s.substring(7);
        }

        String[] ret = s.split("\\.");
        Integer[] test = getVersionIntCore(ret);
        if (test == null) {
            Log.e("can't parse '" + s + "', fallback to default...");
            return PYVERcached = PYVER;
        }
        Log.i("Python3 version was determined from cmd output:" + s);
        return PYVERcached = ret;
    }

    private Integer[] getVersionInt(Context ctx) {
        String[] seq = getVersionSeq(ctx);
        Integer[] ret = getVersionIntCore(seq);
        if (ret != null) {
            return ret;
        }
        return getVersionIntCore(PYVER);
    }

    private Integer[] getVersionIntCore(String[] seq) {
        final int N = 3;
        if (seq == null) {return null;}
        if (seq.length < N) {return null;}

        Integer[] ret = new Integer[N];
        for (int i = 0; i < N; i++) {
            Integer n;
            String s = seq[i];
            try {
                n = Integer.parseInt(s);
            } catch (Exception ex) {
                return getVersionIntCore(PYVER);
            }
            ret[i] = n;
        }
        return ret;
    }

    private String getVersion12(Context ctx) {
        String[] seq = getVersionSeq(ctx);
        return seq[0] + "." + seq[1];
    }

    private String getVersion123(Context ctx) {
        String[] seq = getVersionSeq(ctx);
        return seq[0] + "." + seq[1] + "." + seq[2];
    }

    @Override
    protected String pathBin() {
        return "/bin/python";
    }

    @Override
    protected String pathShlib() {
        return "/lib";
    }

    @Override
    protected String pathEgg() {
        String py12 = getVersion12(null);
        return this.pathShlib() + "/python" + py12 + "/egg-info";
    }

    @Override
    protected String pathSitepkgs() {
        String py12 = getVersion12(null);
        return this.pathShlib() + "/python" + py12 + "/site-packages";
    }

    @Override
    protected String pathDynload() {
        String py12 = getVersion12(null);
        return this.pathShlib() + "/python" + py12 + "/lib-dynload";
    }

  @Override
  public String getBaseInstallUrl() {
    return Python3Urls.URL_BIN;
  }

  @Override
  protected String urlSrc() {
    return Python3Urls.URL_SRC;
  };

  @Override
  protected String pathVersion() {
    return "python3-alpha/LATEST_VERSION";
  };

  @Override
  public String getExtension() {
        if (getPyExtPreffered() == 2) {
            return ".py3";
        }
        if (isPython2Installed()) {
            return ".py3";
        }
        return ".py";
  }

  @Override
  public String getName() {
    return "python3";
  }

  @Override
  public String getNiceName() {
        String py123 = getVersion123(null);
        return "Python " + py123;
  }

  @Override
  public File getBinary(Context context) {
        File f;
        f = new File(context.getFilesDir(), PYTHON_BIN);
      return f;
    // return new File(getExtrasPath(context), PYTHON_BIN);
  }

  @Override
  public Map<String, String> getEnvironmentVariables(Context context) {
    Map<String, String> values = new HashMap<String, String>();
        String home = getHome(context);
    String pylibs = getExtras();

        // current 3.4.? binary does not recognize PYTHONHOME collectly...why..
        Integer[] seq = getVersionInt(context);
        if ((seq[0] >= 3) && (seq[1] >= 6)) {
            values.put(
                PythonConstants.ENV_HOME,
                pylibs + ":" + new File(home, "python3").getAbsolutePath());
        }
        String sitelibs = new File(getExtrasRoot(), "local").getAbsolutePath();
        values.put(PythonConstants.ENV_USERBASE, sitelibs);
        sitelibs = new File(sitelibs, "lib").getAbsolutePath();

        values.put(PythonConstants.ENV_LD, home + pathShlib());
    values.put(PythonConstants.ENV_PATH,
               pylibs + ":" +
               sitelibs + ":" +                     // for USERBASE (pip)
               home + this.pathShlib() + ":" +
               home + this.pathSitepkgs() + ":" +
               home + this.pathDynload());
    values.put(PythonConstants.ENV_EGGS, home + this.pathEgg());
    values.put(PythonConstants.ENV_EXTRAS, getExtrasRoot());
    String temp = context.getCacheDir().getAbsolutePath();
    values.put(PythonConstants.ENV_TEMP, temp);
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
}
