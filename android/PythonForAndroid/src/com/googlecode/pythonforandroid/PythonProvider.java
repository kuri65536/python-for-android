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

package com.googlecode.pythonforandroid;

import android.content.SharedPreferences;
import android.content.SharedPreferences.Editor;
import android.content.res.Resources.NotFoundException;
import android.preference.PreferenceManager;
import android.util.Log;

import com.googlecode.android_scripting.FileUtils;
import com.googlecode.android_scripting.interpreter.InterpreterConstants;
import com.googlecode.android_scripting.interpreter.InterpreterDescriptor;
import com.googlecode.android_scripting.interpreter.InterpreterProvider;

import java.io.File;
import java.io.IOException;

import javax.xml.parsers.DocumentBuilder;
import javax.xml.parsers.DocumentBuilderFactory;
import javax.xml.parsers.ParserConfigurationException;

import org.w3c.dom.Document;
import org.w3c.dom.Element;
import org.w3c.dom.Node;
import org.w3c.dom.NodeList;
import org.xml.sax.SAXException;

public class PythonProvider extends InterpreterProvider {

  static String TAG = "PY4A-PROVIDER";

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

  private void sanitizeEnvironment() throws ParserConfigurationException, NotFoundException,
      SAXException, IOException {
    File files = getContext().getFilesDir().getAbsoluteFile();
    File flibs = new File(files, "lib");
    File fbin = new File(files, "bin");

    if (flibs.isDirectory() && flibs.list().length > 0 && fbin.isDirectory()
        && fbin.list().length > 0) {
      return;
    }
    
    new File(files, "lib/python2.6/site-packages/").mkdirs();

    File libs = new File(files.getParentFile(), "lib");

    DocumentBuilderFactory dbf = DocumentBuilderFactory.newInstance();
    DocumentBuilder db = dbf.newDocumentBuilder();
    Document doc =
        db.parse(getContext().getResources().openRawResource(
            com.googlecode.pythonforandroid.R.raw.files));
    doc.getDocumentElement().normalize();
    Log.v(TAG, "Root element " + doc.getDocumentElement().getNodeName());
    NodeList nodeLst = doc.getElementsByTagName("files").item(0).getChildNodes();
    Log.v(TAG, "Information of all files " + nodeLst.getLength());

    for (int s = 0; s < nodeLst.getLength(); s++) {
      Node fstNode = nodeLst.item(s);
      if (fstNode.getNodeType() == Node.ELEMENT_NODE) {
        Element fstElmnt = (Element) fstNode;
        File fdest = new File(files, fstElmnt.getAttribute("target"));
        File fsrc = new File(libs, fstElmnt.getAttribute("src"));
        Log.v(TAG, fdest + " -> " + fsrc);
        try {
          Log.v(TAG, "created folder " + fdest.getParentFile().mkdirs());
          Runtime.getRuntime().exec("ln -s " + fsrc + " " + fdest).waitFor();
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
    try {
      sanitizeEnvironment();
      File files = getContext().getFilesDir().getAbsoluteFile();
      FileUtils.recursiveChmod(files, 0777);
    } catch (NotFoundException e) {
      // TODO Auto-generated catch block
      e.printStackTrace();
    } catch (ParserConfigurationException e) {
      // TODO Auto-generated catch block
      e.printStackTrace();
    } catch (SAXException e) {
      // TODO Auto-generated catch block
      e.printStackTrace();
    } catch (IOException e) {
      // TODO Auto-generated catch block
      e.printStackTrace();
    } catch (Exception e) {
      // TODO Auto-generated catch block
      e.printStackTrace();
    }
    return new PythonDescriptor();
  }
}
