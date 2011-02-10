package com.googlecode.pythonforandroid;

import android.content.Context;
import android.content.SharedPreferences;
import android.content.SharedPreferences.Editor;

import com.googlecode.android_scripting.AsyncTaskListener;
import com.googlecode.android_scripting.InterpreterUninstaller;
import com.googlecode.android_scripting.exception.Sl4aException;
import com.googlecode.android_scripting.interpreter.InterpreterDescriptor;

public class PythonUninstaller extends InterpreterUninstaller {

  public PythonUninstaller(InterpreterDescriptor descriptor, Context context,
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

    return true;
  }
}
