package com.googlecode.pythonforandroid;

import android.content.Context;
import android.content.SharedPreferences;
import android.content.SharedPreferences.Editor;
import android.os.AsyncTask;

import com.googlecode.android_scripting.AsyncTaskListener;
import com.googlecode.android_scripting.InterpreterInstaller;
import com.googlecode.android_scripting.Log;
import com.googlecode.android_scripting.exception.Sl4aException;
import com.googlecode.android_scripting.interpreter.InterpreterConstants;
import com.googlecode.android_scripting.interpreter.InterpreterDescriptor;

import java.io.File;

public class PythonInstaller extends InterpreterInstaller {

  public PythonInstaller(InterpreterDescriptor descriptor, Context context,
      AsyncTaskListener<Boolean> listener) throws Sl4aException {
    super(descriptor, context, listener);
  }

  @Override
  protected boolean setup() {
    File tmp =
        new File(InterpreterConstants.SDCARD_ROOT + getClass().getPackage().getName()
            + InterpreterConstants.INTERPRETER_EXTRAS_ROOT, mDescriptor.getName() + "/tmp");
    if (!tmp.isDirectory()) {
      try {
        tmp.mkdir();
      } catch (SecurityException e) {
        Log.e(mContext, "Setup failed.", e);
        return false;
      }
    }
    return true;
  }

  private void saveVersionSetting(String key, int value) {
    SharedPreferences storage = mContext.getSharedPreferences("python-installer", 0);
    Editor editor = storage.edit();
    editor.putInt(key, value);
    editor.commit();
  }

  @Override
  protected AsyncTask<Void, Integer, Long> extractInterpreter() throws Sl4aException {
    saveVersionSetting("interpreter", ((PythonDescriptor) mDescriptor).getVersion(true));
    return super.extractInterpreter();
  }

  @Override
  protected AsyncTask<Void, Integer, Long> extractInterpreterExtras() throws Sl4aException {
    saveVersionSetting("extras", ((PythonDescriptor) mDescriptor).getExtrasVersion(true));
    return super.extractInterpreterExtras();
  }

  @Override
  protected AsyncTask<Void, Integer, Long> extractScripts() throws Sl4aException {
    saveVersionSetting("scripts", ((PythonDescriptor) mDescriptor).getScriptsVersion(true));
    return super.extractScripts();
  }
}
