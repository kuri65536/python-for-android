package com.googlecode.pythonforandroid;

import android.content.SharedPreferences;
import android.content.SharedPreferences.Editor;
import android.preference.PreferenceManager;
import android.util.Log;

import com.googlecode.android_scripting.FileUtils;
import com.googlecode.android_scripting.interpreter.InterpreterConstants;
import com.googlecode.android_scripting.interpreter.InterpreterDescriptor;
import com.googlecode.android_scripting.interpreter.InterpreterProvider;

import java.io.File;
import java.io.IOException;

public class PythonProvider extends InterpreterProvider {

  @Override
  public boolean onCreate() {
    SharedPreferences mPreferences;
    mPreferences = PreferenceManager.getDefaultSharedPreferences(getContext());
    if (!mPreferences.getBoolean(InterpreterConstants.INSTALLED_PREFERENCE_KEY, false)) {
      Editor editor = mPreferences.edit();
      editor.putBoolean(InterpreterConstants.INSTALLED_PREFERENCE_KEY, true);
      editor.commit();
    }
    return super.onCreate();
  }

  private void sanitizeEnvironment() {
    File files = getContext().getFilesDir().getAbsoluteFile();
    File flibs = new File(files, "lib");
    File fbin = new File(files, "bin");
    File libs = null;
    if (flibs.isDirectory() && flibs.list().length > 0 && fbin.isDirectory()
        && fbin.list().length > 0) {
      return;
    }

    libs = new File(files.getParentFile(), "lib");

    for (File i : libs.listFiles()) {
      if (i.isFile() && i.getName().startsWith("lib_")) {
        String path = i.getName().substring(4, 7);
        File parent = new File(files, path);
        parent.mkdirs();
        File target = new File(parent, i.getName().substring(8).replace(".so", "."));
        try {
          Log.v("PY4A", "Symlink " + target + " -> " + i);
          Runtime.getRuntime().exec("ln -s " + i + " " + target).waitFor();
        } catch (IOException e) {
          e.printStackTrace();
        } catch (InterruptedException e) {
          e.printStackTrace();
        }
      }
    }

    try {
      FileUtils.recursiveChmod(files, 0777);
    } catch (Exception e) {
      // TODO Auto-generated catch block
      e.printStackTrace();
    }
  }

  @Override
  protected InterpreterDescriptor getDescriptor() {
    sanitizeEnvironment();
    return new PythonDescriptor();
  }
}
