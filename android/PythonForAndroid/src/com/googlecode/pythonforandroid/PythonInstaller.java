package com.googlecode.pythonforandroid;

import android.content.Context;
import android.content.SharedPreferences;
import android.content.SharedPreferences.Editor;
import android.os.AsyncTask;

import com.googlecode.android_scripting.AsyncTaskListener;
import com.googlecode.android_scripting.InterpreterInstaller;
import com.googlecode.android_scripting.IoUtils;
import com.googlecode.android_scripting.Log;
import com.googlecode.android_scripting.exception.Sl4aException;
import com.googlecode.android_scripting.interpreter.InterpreterConstants;
import com.googlecode.android_scripting.interpreter.InterpreterDescriptor;

import java.io.File;
import java.io.FileNotFoundException;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.InputStream;

public class PythonInstaller extends InterpreterInstaller {
  private PythonDescriptor mPyDescriptor;

  public PythonInstaller(InterpreterDescriptor descriptor, Context context,
      AsyncTaskListener<Boolean> listener) throws Sl4aException {
    super(descriptor, context, listener);
    mPyDescriptor = (PythonDescriptor) mDescriptor;
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

  /*
   * private AsyncTask<Void, Integer, Long> genericDownload(int raw, String archive) throws
   * MalformedURLException { if (mPyDescriptor.getOffline()) { return new VoidDownloader(archive,
   * mInterpreterRoot, mContext.getResources().openRawResource( raw)); } int v =
   * mPyDescriptor.getVersion(true); if (v == -1 || v ==
   * Integer.parseInt(mContext.getString(R.string.python_interpreter))) { return new
   * VoidDownloader(mPyDescriptor.getInterpreterArchiveName(), mInterpreterRoot,
   * mContext.getResources().openRawResource(R.raw.python)); } return null; }
   * 
   * @Override protected AsyncTask<Void, Integer, Long> downloadInterpreter() throws
   * MalformedURLException { AsyncTask<Void, Integer, Long> out = genericDownload(R.raw.python,
   * mPyDescriptor.getInterpreterArchiveName()); if (out != null) { return out; } return
   * super.downloadInterpreter(); }
   * 
   * @Override protected AsyncTask<Void, Integer, Long> downloadInterpreterExtras() throws
   * MalformedURLException { AsyncTask<Void, Integer, Long> out =
   * genericDownload(R.raw.python_extras, mPyDescriptor.getExtrasArchiveName()); if (out != null) {
   * return out; } return super.downloadInterpreterExtras(); }
   * 
   * @Override protected AsyncTask<Void, Integer, Long> downloadScripts() throws
   * MalformedURLException { AsyncTask<Void, Integer, Long> out =
   * genericDownload(R.raw.python_scripts, mPyDescriptor.getScriptsArchiveName()); if (out != null)
   * { return out; } return super.downloadScripts();
   * 
   * }
   * 
   * @Override protected AsyncTask<Void, Integer, Long> extractInterpreter() throws Sl4aException {
   * saveVersionSetting("interpreter", ((PythonDescriptor) mDescriptor).getVersion(true)); return
   * super.extractInterpreter(); }
   * 
   * @Override protected AsyncTask<Void, Integer, Long> extractInterpreterExtras() throws
   * Sl4aException { saveVersionSetting("extras", ((PythonDescriptor)
   * mDescriptor).getExtrasVersion(true)); return super.extractInterpreterExtras(); }
   * 
   * @Override protected AsyncTask<Void, Integer, Long> extractScripts() throws Sl4aException {
   * saveVersionSetting("scripts", ((PythonDescriptor) mDescriptor).getScriptsVersion(true)); return
   * super.extractScripts(); }
   */

  @Override
  protected void finish(boolean result) {
    super.finish(result);
    mPyDescriptor.setOffline(false);
  }

  private class VoidDownloader extends AsyncTask<Void, Integer, Long> {
    private final File mFile;
    private final InputStream mIn;

    public VoidDownloader(String filename, String out, InputStream inp) {
      super();
      mFile = new File(out, filename);
      mIn = inp;
    }

    @Override
    protected Long doInBackground(Void... params) {
      int bytesCopied = 0;
      try {
        bytesCopied = IoUtils.copy(mIn, new FileOutputStream(mFile));
      } catch (FileNotFoundException e) {
        e.printStackTrace();
      } catch (IOException e) {
        e.printStackTrace();
      } catch (Exception e) {
        e.printStackTrace();
      }
      return new Long(bytesCopied);
    }

  }
}
