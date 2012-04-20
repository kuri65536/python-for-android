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

import android.app.AlertDialog;
import android.app.Dialog;
import android.app.ProgressDialog;
import android.content.ComponentName;
import android.content.Context;
import android.content.DialogInterface;
import android.content.Intent;
import android.content.SharedPreferences;
import android.content.SharedPreferences.Editor;
import android.net.Uri;
import android.os.AsyncTask;
import android.os.Bundle;
import android.os.Environment;
import android.os.Handler;
import android.os.Message;
import android.preference.PreferenceManager;
import android.view.Menu;
import android.view.MenuItem;
import android.view.View;
import android.view.View.OnClickListener;
import android.view.ViewGroup.LayoutParams;
import android.view.ViewGroup.MarginLayoutParams;
import android.view.Window;
import android.widget.Button;
import android.widget.TextView;
import android.widget.Toast;

import com.googlecode.android_scripting.AsyncTaskListener;
import com.googlecode.android_scripting.FileUtils;
import com.googlecode.android_scripting.InterpreterInstaller;
import com.googlecode.android_scripting.InterpreterUninstaller;
import com.googlecode.android_scripting.Log;
import com.googlecode.android_scripting.activity.Main;
import com.googlecode.android_scripting.exception.Sl4aException;
import com.googlecode.android_scripting.interpreter.InterpreterConstants;
import com.googlecode.android_scripting.interpreter.InterpreterDescriptor;
import com.googlecode.android_scripting.interpreter.InterpreterUtils;

import java.io.BufferedInputStream;
import java.io.BufferedOutputStream;
import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileNotFoundException;
import java.io.FileOutputStream;
import java.io.FileReader;
import java.io.FileWriter;
import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import java.net.URL;
import java.util.ArrayList;
import java.util.Enumeration;
import java.util.List;
import java.util.Properties;
import java.util.Vector;
import java.util.zip.ZipEntry;
import java.util.zip.ZipFile;

/**
 * Python Installer. Incorporates module installer.
 * 
 * The module installer reads a zip file previously downloaded into "download", and unpacks it. If
 * the module contains shared libraries (*.so) then the module is unpacked into data, other installs
 * in extras.
 * 
 * Typically, these will be /data/data/com.googlecode.pythonforandroid/files/python/lib/python3.2
 * and /sdcard/com.googlecode.pythonforandroid/extras respectively.
 * 
 * Egg files are just copied into
 * /data/data/com.googlecode.pythonforandroid/files/python/lib/python3.2
 * 
 * @author Damon
 * @author Robbie Matthews (rjmatthews62@gmail.com)
 * @author Manuel Naranjo (manuel@aircable.net)
 */

// TODO:(Robbie) The whole Import Module is more of a proof of concept than a fully realised
// process. Needs some means of checking that these are properly formatted zip files, and probably a
// means of uninstalling as well. Import handling could well be a separate activity, too.
public class Python3Main extends Main {
  Button mButtonInstallScripts;
  Button mButtonInstallModules;
  Button mButtonUninstallModule;
  File mDownloads;

  private Dialog mDialog;
  protected String mModule;
  private CharSequence[] mList;
  private ProgressDialog mProgress;
  private boolean mPromptResult;

  private static enum MenuId {
    BROWSER, SL4A, VERSION;
    public int getId() {
      return ordinal() + Menu.FIRST;
    }
  }

  private String readFirstLine(File target) {
    BufferedReader in;
    String result;
    try {
      in = new BufferedReader(new FileReader(target));
      result = in.readLine();
      if (result == null) {
        result = "";
      }
      in.close();
    } catch (Exception e) {
      e.printStackTrace();
      result = "";
    }
    return result;
  }

  final Handler mModuleHandler = new Handler() {

    @Override
    public void handleMessage(Message message) {
      Bundle bundle = message.getData();
      boolean running = bundle.getBoolean("running");
      if (running) {
        if (bundle.containsKey("max")) {
          mProgress.setProgress(0);
          mProgress.setMax(bundle.getInt("max"));
        } else if (bundle.containsKey("pos")) {
          mProgress.setProgress(bundle.getInt("pos"));
        } else if (bundle.containsKey("message")) {
          mProgress.setMessage(bundle.getString("message"));
        } else {
          mProgress.incrementProgressBy(1);
        }
      } else {
        mProgress.dismiss();
        String info = message.getData().getString("info");
        if (info != null) {
          showMessage("Import Module", info);
        }
      }
    }
  };

  private Button mButtonBrowse;
  private File mFrom;
  private File mSoPath;
  private File mPythonPath;
  private File mEggPath;
  private Python3Descriptor mDescriptor;
  private TextView mVersions;

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

  @Override
  protected void onResume() {
    String s;
    super.onResume();
    Intent intent = getIntent();
    if (intent.getData() != null) {
      s = intent.getData().getPath();
      Toast.makeText(this, s, Toast.LENGTH_SHORT).show();
      File file = new File(intent.getData().getPath());
      if (file.exists()) {
        performImport(file, file.getName());
      }
    }
  }

  @Override
  protected void initializeViews() {
    super.initializeViews();
    // mButton.setVisibility(View.GONE);

    mDownloads = FileUtils.getExternalDownload();
    if (!mDownloads.exists()) {
      for (File file : new File(Environment.getExternalStorageDirectory().getAbsolutePath())
          .listFiles()) {
        if (file.isDirectory()) {
          if (file.getName().toLowerCase().startsWith("download")) {
            mDownloads = file;
            break;
          }
        }
      }
    }

    MarginLayoutParams marginParams =
        new MarginLayoutParams(LayoutParams.FILL_PARENT, LayoutParams.WRAP_CONTENT);
    final float scale = getResources().getDisplayMetrics().density;
    int marginPixels = (int) (MARGIN_DIP * scale + 0.5f);
    marginParams.setMargins(marginPixels, marginPixels, marginPixels, marginPixels);

    mButtonInstallScripts = new Button(this);
    mButtonInstallScripts.setLayoutParams(marginParams);
    mButtonInstallScripts.setText("Install Python3");
    // mLayout.addView(mButtonInstallScripts);
    mButtonInstallScripts.setOnClickListener(new OnClickListener() {
      public void onClick(View v) {
        if (mCurrentTask != null) {
          return;
        }
        getWindow().setFeatureInt(Window.FEATURE_INDETERMINATE_PROGRESS,
            Window.PROGRESS_VISIBILITY_ON);
        mCurrentTask = RunningTask.INSTALL;
        InterpreterInstaller installTask;
        try {
          installTask = getInterpreterInstaller(mDescriptor, Python3Main.this, mTaskListener);
        } catch (Sl4aException e) {
          Log.e(Python3Main.this, e.getMessage(), e);
          return;
        }
        installTask.execute();
      }
    });

    mButtonInstallModules = new Button(this);
    mButtonInstallModules.setLayoutParams(marginParams);
    mButtonInstallModules.setText("Import Modules");
    mLayout.addView(mButtonInstallModules);
    mButtonInstallModules.setOnClickListener(new OnClickListener() {
      public void onClick(View v) {
        doImportModule();
      }
    });

    mButtonBrowse = new Button(this);
    mButtonBrowse.setLayoutParams(marginParams);
    mButtonBrowse.setText("Browse Modules");
    mLayout.addView(mButtonBrowse);
    mButtonBrowse.setOnClickListener(new OnClickListener() {
      public void onClick(View v) {
        doBrowseModule();
      }
    });

    mButtonUninstallModule = new Button(this);
    mButtonUninstallModule.setLayoutParams(marginParams);
    mButtonUninstallModule.setText("Uninstall Module");
    mLayout.addView(mButtonUninstallModule);
    mButtonUninstallModule.setOnClickListener(new OnClickListener() {
      public void onClick(View v) {
        doDeleteModule();
      }
    });

    mVersions = new TextView(this);
    mVersions.setLayoutParams(marginParams);
    updateVersions();
    mLayout.addView(mVersions);
    doCheckVersion();
  }

  void updateVersions() {
    Python3Descriptor descriptor = new Python3Descriptor();
    descriptor.setSharedPreferences(mPreferences);
    mVersions.setText("Version Available: Bin: " + descriptor.getVersion() + " Extra: "
        + descriptor.getExtrasVersion() + " Scripts: " + descriptor.getScriptsVersion() + "\n"
        + "Version Installed: " + getInstalledVersion());

  }

  @Override
  protected void setInstalled(boolean isInstalled) {
    super.setInstalled(isInstalled);
    updateVersions();
  }

  private String getInstalledVersion() {
    String result;
    int version = 0;
    int extrasVersion = 0;
    int scriptsVersion = 0;

    SharedPreferences preferences = PreferenceManager.getDefaultSharedPreferences(this);
    if (!preferences.getBoolean(InterpreterConstants.INSTALLED_PREFERENCE_KEY, false)) {
      result = "Not Installed";
    } else if (preferences.contains(Python3Constants.INSTALLED_VERSION_KEY)) {
      version = preferences.getInt(Python3Constants.INSTALLED_VERSION_KEY, 0);
      extrasVersion = preferences.getInt(Python3Constants.INSTALLED_EXTRAS_KEY, 0);
      scriptsVersion = preferences.getInt(Python3Constants.INSTALLED_SCRIPTS_KEY, 0);
      result = "Bin: " + version + " Extra: " + extrasVersion + " Scripts: " + scriptsVersion;
    } else {
      result = "Unknown";
    }
    return result;
  }

  protected void doBrowseModule() {
    Intent intent =
        new Intent(Intent.ACTION_VIEW,
            Uri.parse("http://code.google.com/p/python-for-android/wiki/Modules"));
    startActivity(intent);
  }

  public void doImportModule() {
    AlertDialog.Builder builder = new AlertDialog.Builder(this);
    DialogInterface.OnClickListener buttonListener = new DialogInterface.OnClickListener() {

      @Override
      public void onClick(DialogInterface dialog, int which) {
        mDialog.dismiss();
        if (which == DialogInterface.BUTTON_NEUTRAL) {
          showMessage("Import Module",
              "This will take a previously downloaded (and appropriately formatted) "
                  + "python external module zip or egg file.\nSee sl4a wiki for more defails.\n"
                  + "Looking for files in \n" + mDownloads);
        }
      }
    };

    List<String> flist = new Vector<String>();
    for (File f : mDownloads.listFiles()) {
      if (f.getName().endsWith(".zip") || f.getName().endsWith(".egg")) {
        flist.add(f.getName());
      }
    }

    builder.setTitle("Import Module");

    mList = flist.toArray(new CharSequence[flist.size()]);
    builder.setItems(mList, new DialogInterface.OnClickListener() {

      @Override
      public void onClick(DialogInterface dialog, int which) {
        mModule = (String) mList[which];
        performImport(mModule);
        mDialog.dismiss();
      }
    });
    builder.setNegativeButton("Cancel", buttonListener);
    builder.setNeutralButton("Help", buttonListener);
    mModule = null;
    mDialog = builder.show();
    if (mModule != null) {
    }
  }

  public void doDeleteModule() {
    mEggPath = new File(InterpreterUtils.getInterpreterRoot(this), "python3/egg-info");
    AlertDialog.Builder builder = new AlertDialog.Builder(this);
    DialogInterface.OnClickListener buttonListener = new DialogInterface.OnClickListener() {

      @Override
      public void onClick(DialogInterface dialog, int which) {
        mDialog.dismiss();
        if (which == DialogInterface.BUTTON_NEUTRAL) {
          showMessage("Uninstall Module",
              "This will let you delete a module you got installed from an egg file");
        }
      }
    };

    List<String> flist = new Vector<String>();
    for (File f : mEggPath.listFiles()) {
      if (f.getName().endsWith(".egg")) {
        flist.add(f.getName().replace(".egg", ""));
      }
    }

    builder.setTitle("Installed Modules");

    mList = flist.toArray(new CharSequence[flist.size()]);
    builder.setItems(mList, new DialogInterface.OnClickListener() {

      @Override
      public void onClick(DialogInterface dialog, int which) {
        mModule = (String) mList[which];
        performUninstall(mModule);
        mDialog.dismiss();
      }
    });
    builder.setNegativeButton("Cancel", buttonListener);
    builder.setNeutralButton("Help", buttonListener);
    mModule = null;
    mDialog = builder.show();
    if (mModule != null) {
    }
  }

  protected void performImport(String module) {
    performImport(new File(mDownloads, mModule), module);
  }

  protected void performImport(File sourceFile, String module) {
    mModule = module;
    mFrom = sourceFile;
    mSoPath =
        new File(InterpreterUtils.getInterpreterRoot(this), "python3/lib/python3.2/lib-dynload");
    mEggPath = new File(InterpreterUtils.getInterpreterRoot(this), "python3/egg-info");
    mPythonPath = new File(mDescriptor.getEnvironmentVariables(this).get("PY4A_EXTRAS"), "python3");

    prompt("Install module " + module, new DialogInterface.OnClickListener() {

      @Override
      public void onClick(DialogInterface dialog, int which) {
        if (which == AlertDialog.BUTTON_POSITIVE) {
          if (mModule.toLowerCase().endsWith(".egg")) {
            copy(new File(mSoPath, mModule), mFrom);
            try {
              File out =
                  new File(InterpreterUtils.getInterpreterRoot(Python3Main.this),
                      "lib/python3.2/site-packages/" + mModule + ".pth");
              FileOutputStream fout = new FileOutputStream(out);
              fout.write(new File(mSoPath, mModule).getAbsolutePath().getBytes());
              fout.close();
              FileUtils.recursiveChmod(
                  new File(InterpreterUtils.getInterpreterRoot(Python3Main.this), "lib"), 0777);
              FileUtils.recursiveChmod(
                  new File(InterpreterUtils.getInterpreterRoot(Python3Main.this), "python3"), 0777);
              showMessage("Success", "Sucessfully installed");
              return;
            } catch (FileNotFoundException e) {
              // TODO Auto-generated catch block
              e.printStackTrace();
            } catch (IOException e) {
              // TODO Auto-generated catch block
              e.printStackTrace();
            } catch (Exception e) {
              // TODO Auto-generated catch block
              e.printStackTrace();
            }

            showMessage("Failure", "Failed while installing");
          } else {
            extract("Extracting " + mModule, mFrom, mPythonPath, mSoPath, mEggPath);
          }
        }
      }
    });
  }

  protected void performUninstall(String module) {
    mModule = module;
    mEggPath = new File(InterpreterUtils.getInterpreterRoot(this), "python3/egg-info");
    mFrom = new File(mEggPath, module + ".egg");
    mSoPath =
        new File(InterpreterUtils.getInterpreterRoot(this), "python3/lib/python3.2/lib-dynload");

    mPythonPath = new File(mDescriptor.getEnvironmentVariables(this).get("PY4A_EXTRAS"));

    prompt("Uninstall module " + module, new DialogInterface.OnClickListener() {

      @Override
      public void onClick(DialogInterface dialog, int which) {
        if (which == AlertDialog.BUTTON_POSITIVE) {
          remove("Deleting " + mModule, mFrom, mPythonPath, mSoPath, mEggPath);
        }
      }
    });
  }

  protected void extract(String caption, File from, File pypath, File sopath, File egginfo) {
    mProgress = showProgress(caption);
    Thread t = new RunExtract(caption, from, pypath, sopath, mModuleHandler, egginfo);
    t.start();
  }

  protected void copy(File target, File from) {
    try {
      InputStream input = new BufferedInputStream(new FileInputStream(from));
      target.getParentFile().mkdirs();
      OutputStream output = new BufferedOutputStream(new FileOutputStream(target));
      byte[] buf = new byte[1024];
      int len;

      while ((len = input.read(buf)) > 0) {
        output.write(buf, 0, len);
      }
      output.close();
      input.close();
      FileUtils.recursiveChmod(target.getParentFile(), 0777);
    } catch (FileNotFoundException e) {
      // TODO Auto-generated catch block
      e.printStackTrace();
    } catch (IOException e) {
      // TODO Auto-generated catch block
      e.printStackTrace();
    } catch (Exception e) {
      // TODO Auto-generated catch block
      e.printStackTrace();
    }

  }

  protected void remove(String caption, File from, File pypath, File sopath, File egginfo) {
    mProgress = showProgress(caption);
    Thread t = new RunDelete(caption, from, pypath, sopath, mModuleHandler, egginfo);
    t.start();
  }

  protected ProgressDialog showProgress(String caption) {
    ProgressDialog b = new ProgressDialog(this);
    b.setTitle(caption);
    b.setProgressStyle(ProgressDialog.STYLE_HORIZONTAL);
    b.show();
    return b;
  }

  protected void showMessage(String title, String message) {
    AlertDialog.Builder builder = new AlertDialog.Builder(this);
    builder.setTitle(title);
    builder.setMessage(message);
    builder.setNeutralButton("OK", null);
    builder.show();
  }

  protected boolean prompt(String message, DialogInterface.OnClickListener btnlisten) {
    mPromptResult = false;
    AlertDialog.Builder builder = new AlertDialog.Builder(this);
    builder.setTitle("Python Installer");
    builder.setMessage(message);
    builder.setNegativeButton("Cancel", btnlisten);
    builder.setPositiveButton("OK", btnlisten);
    builder.show();
    return mPromptResult;
  }

  @Override
  public boolean onCreateOptionsMenu(Menu menu) {
    menu.add(Menu.NONE, MenuId.BROWSER.getId(), Menu.NONE, "File Browser").setIcon(
        android.R.drawable.ic_menu_myplaces);
    menu.add(Menu.NONE, MenuId.SL4A.getId(), Menu.NONE, "SL4A").setIcon(R.drawable.sl4a_logo_32);
    menu.add(Menu.NONE, MenuId.VERSION.getId(), Menu.NONE, "Check Version").setIcon(
        android.R.drawable.ic_menu_info_details);
    return true;
  }

  @Override
  public boolean onOptionsItemSelected(MenuItem item) {
    Intent intent;
    int id = item.getItemId();
    if (MenuId.BROWSER.getId() == id) {
      intent = new Intent(this, FileBrowser.class);
      intent.setAction(Python3Constants.ACTION_FILE_BROWSER);
      // intent.setFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
      startActivity(intent);
    } else if (MenuId.SL4A.getId() == id) {
      intent = new Intent();
      intent.setComponent(new ComponentName(Python3Constants.SL4A, Python3Constants.SL4A_MANAGER));
      try {
        startActivity(intent);
      } catch (Exception e) {
        showMessage("Py4A", "SL4A may not be installed.");
      }
    } else if (MenuId.VERSION.getId() == id) {
      doCheckVersion();
    }
    return true;
  }

  private void doCheckVersion() {
    (new CheckVersion(this)).execute();
  }

  class RunExtract extends Thread {
    String caption;
    File from;
    File sopath;
    File pypath;
    File egginfo;
    Handler mHandler;

    RunExtract(String caption, File from, File pypath, File sopath, Handler h, File egginfo) {
      this.caption = caption;
      this.from = from;
      this.pypath = pypath;
      this.sopath = sopath;
      this.egginfo = egginfo;
      mHandler = h;
    }

    @Override
    public void run() {
      byte[] buf = new byte[4096];
      boolean isInfo = false;
      List<ZipEntry> list = new ArrayList<ZipEntry>();
      Vector<String> installed = new Vector<String>();
      boolean hasSo = false;
      try {
        ZipFile zipfile = new ZipFile(from);
        int cnt = 0;
        sendmsg(true, "max", zipfile.size());
        Enumeration<? extends ZipEntry> entries = zipfile.entries();
        while (entries.hasMoreElements()) {
          ZipEntry ex = entries.nextElement();
          if (ex.getName().endsWith(".so")) {
            hasSo = true;
          }
          list.add(ex);
        }
        for (ZipEntry entry : list) {
          cnt += 1;
          if (entry.isDirectory()) {
            continue;
          }

          File destinationPath;
          File destinationFile;
          isInfo = entry.getName().contains("EGG-INFO");

          if (isInfo) {
            destinationPath = new File(egginfo, from.getName());
            destinationFile = new File(destinationPath, entry.getName().split("/", 2)[1]);
          } else {
            // destinationPath = entry.getName().endsWith(".so") ? sopath : pypath;
            // Python does not cope well with splitting *.so and normal files. Sadly.
            // At the moment, if we have an *.so, we will copy entire library to main memory.
            destinationPath = hasSo ? sopath : pypath;
            destinationFile = new File(destinationPath, entry.getName());
          }

          FileUtils.makeDirectories(destinationFile.getParentFile(), 0755);
          sendmsg(true, "pos", cnt);
          OutputStream output = new BufferedOutputStream(new FileOutputStream(destinationFile));
          InputStream input = zipfile.getInputStream(entry);
          int len;
          while ((len = input.read(buf)) > 0) {
            output.write(buf, 0, len);
          }
          input.close();
          output.flush();
          output.close();

          if (entry.getName().endsWith(".py")) {
            if (readFirstLine(destinationFile).contains("__bootstrap__")) {
              // don't include autogenerated bootstrap, not useful for us
              destinationFile.delete();
              continue;
            }
          }

          if (!isInfo) {
            installed.add(destinationFile.getAbsolutePath());
          }
          destinationFile.setLastModified(entry.getTime());
          FileUtils.chmod(destinationFile, entry.getName().endsWith(".so") ? 0755 : 0644);

        }

        FileWriter fstream =
            new FileWriter(new File(new File(egginfo, from.getName()), "files.txt"));
        BufferedWriter out = new BufferedWriter(fstream);
        for (String line : installed) {
          out.write(line + "\n");
        }
        out.close();

        sendmsg(false, "Success");
      } catch (Exception entry) {
        sendmsg(false, "Error" + entry);
      }
    }

    private void sendmsg(boolean running, String info) {
      Message message = mHandler.obtainMessage();
      Bundle bundle = new Bundle();
      bundle.putBoolean("running", running);
      if (info != null) {
        bundle.putString("info", info);
      }
      message.setData(bundle);
      mHandler.sendMessage(message);
    }

    private void sendmsg(boolean running, String key, int value) {
      Message message = mHandler.obtainMessage();
      Bundle bundle = new Bundle();
      bundle.putBoolean("running", running);
      bundle.putInt(key, value);
      message.setData(bundle);
      mHandler.sendMessage(message);
    }
  }

  class RunDelete extends Thread {
    String caption;
    File from;
    File sopath;
    File pypath;
    File egginfo;
    Handler mHandler;

    RunDelete(String caption, File from, File pypath, File sopath, Handler h, File egginfo) {
      this.caption = caption;
      this.from = from;
      this.pypath = pypath;
      this.sopath = sopath;
      this.egginfo = egginfo;
      mHandler = h;
    }

    private void delete(File source) {
      try {
        if (source.exists() && source.isDirectory()) {
          for (File entry : source.listFiles()) {
            if (entry.isDirectory()) {
              delete(entry);
            } else {
              entry.delete();
            }
            System.out.println(entry + " deleted");
          }
          source.delete();
          System.out.println(source.getName() + " deleted");
        }
      } catch (Exception e) {
        e.printStackTrace();
      }
    }

    private void deleteInstalledFiles() {
      BufferedReader in;
      String line;
      File target;
      try {
        in = new BufferedReader(new FileReader(new File(from, "files.txt")));
        while ((line = in.readLine()) != null) {
          target = new File(line);
          if (!target.exists()) {
            continue;
          }
          target.delete();
          System.out.println(target.getAbsolutePath() + " deleted " + target.exists());
        }
      } catch (Exception e) {
        e.printStackTrace();
      }

    }

    @Override
    public void run() {
      sendmsg(true, "max", 4);
      String toplevel = readFirstLine(new File(from, "top_level.txt"));
      deleteInstalledFiles();
      sendmsg(true, "pos", 1);
      delete(new File(sopath, toplevel));
      sendmsg(true, "pos", 2);
      delete(new File(pypath, toplevel));
      sendmsg(true, "pos", 3);
      delete(from);
      sendmsg(true, "pos", 4);

      sendmsg(false, "Success");
    }

    private void sendmsg(boolean running, String info) {
      Message message = mHandler.obtainMessage();
      Bundle bundle = new Bundle();
      bundle.putBoolean("running", running);
      if (info != null) {
        bundle.putString("info", info);
      }
      message.setData(bundle);
      mHandler.sendMessage(message);
    }

    private void sendmsg(boolean running, String key, int value) {
      Message message = mHandler.obtainMessage();
      Bundle bundle = new Bundle();
      bundle.putBoolean("running", running);
      bundle.putInt(key, value);
      message.setData(bundle);
      mHandler.sendMessage(message);
    }
  }

  class CheckVersion extends AsyncTask<Integer, String, Boolean> {
    Python3Main parent;
    int version;
    int extras;
    int scripts;

    CheckVersion(Python3Main parent) {
      super();
      this.parent = parent;
    }

    @Override
    protected void onPostExecute(Boolean result) {
      if (result) {
        Editor e = parent.mPreferences.edit();
        e.putInt(Python3Constants.AVAIL_VERSION_KEY, version);
        e.putInt(Python3Constants.AVAIL_EXTRAS_KEY, extras);
        e.putInt(Python3Constants.AVAIL_SCRIPTS_KEY, scripts);
        e.commit();
        parent.updateVersions();
      }
      super.onPostExecute(result);
    }

    @Override
    protected Boolean doInBackground(Integer... params) {
      publishProgress("Checking website for Updates");
      URL url;
      try {
        // url = new URL("http://python-for-android.googlecode.com/hg/python3-alpha/VERSIONS");
        url = new URL("http://www.mithril.com.au/android/VERSIONS");
        Properties p = new Properties();
        p.load(url.openStream());
        if (p.containsKey("PY34A_VERSION")) {
          version = Integer.valueOf(p.getProperty("PY34A_VERSION"));
          extras = Integer.valueOf(p.getProperty("PY34A_EXTRAS_VERSION"));
          scripts = Integer.valueOf(p.getProperty("PY34A_SCRIPTS_VERSION"));
          publishProgress("Versions Updated");
          return true;
        }
      } catch (Exception e) {
        publishProgress("Error:\n" + e);
      }
      return false;
    }

    @Override
    protected void onProgressUpdate(String... values) {
      if (values.length > 0) {
        Toast.makeText(parent, values[0], Toast.LENGTH_SHORT).show();
      }
      super.onProgressUpdate(values);
    }
  }

}
