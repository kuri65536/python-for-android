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

import android.app.AlertDialog;
import android.app.ListActivity;
import android.app.SearchManager;
import android.content.Context;
import android.content.DialogInterface;
import android.content.Intent;
import android.database.DataSetObserver;
import android.net.Uri;
import android.os.Bundle;
import android.view.ContextMenu;
import android.view.KeyEvent;
import android.view.LayoutInflater;
import android.view.Menu;
import android.view.MenuItem;
import android.view.View;
import android.view.ViewGroup;
import android.view.ContextMenu.ContextMenuInfo;
import android.widget.AdapterView;
import android.widget.BaseAdapter;
import android.widget.EditText;
import android.widget.ImageView;
import android.widget.LinearLayout;
import android.widget.ListView;
import android.widget.TextView;

import com.google.common.base.Predicate;
import com.google.common.collect.Collections2;
import com.google.common.collect.Lists;
import com.googlecode.android_scripting.Constants;
import com.googlecode.android_scripting.FileUtils;
import com.googlecode.android_scripting.Log;
import com.googlecode.android_scripting.interpreter.Interpreter;
import com.googlecode.android_scripting.interpreter.InterpreterConstants;
import com.googlecode.android_scripting.interpreter.InterpreterConfiguration.ConfigurationObserver;

import java.io.File;
import java.net.URLConnection;
import java.util.Arrays;
import java.util.HashMap;
import java.util.List;

/**
 * Manages creation, deletion, and execution of stored scripts.
 * 
 * @author Damon Kohler (damonkohler@gmail.com)
 */
public class FileBrowser extends ListActivity {

  private final static String EMPTY = "";

  private List<File> mScripts;
  private FileBrowserAdapter mAdapter;
  private HashMap<Integer, Interpreter> mAddMenuIds;
  private FileListObserver mObserver;
  private SearchManager mManager;
  private boolean mInSearchResultMode = false;
  private String mQuery = EMPTY;
  private File mCurrentDir;
  private File mBaseDir;
  private File mCurrent;

  // Linux stat constants
  private static final int S_IFMT = 0170000; /* type of file */
  private static final int S_IFLNK = 0120000; /* symbolic link */
  private static final int S_IFREG = 0100000; /* regular */
  private static final int S_IFBLK = 0060000; /* block special */
  private static final int S_IFDIR = 0040000; /* directory */
  private static final int S_IFCHR = 0020000; /* character special */
  private static final int S_IFIFO = 0010000; /* this is a FIFO */
  private static final int S_ISUID = 0004000; /* set user id on execution */
  private static final int S_ISGID = 0002000; /* set group id on execution */

  private static enum MenuId {
    DELETE, HELP, FOLDER_ADD, REFRESH, SEARCH, RENAME, COPY, PLACES;
    public int getId() {
      return ordinal() + Menu.FIRST;
    }
  }

  @Override
  public void onCreate(Bundle savedInstanceState) {
    super.onCreate(savedInstanceState);
    mBaseDir = getFilesDir();
    mCurrentDir = mBaseDir;
    mAdapter = new FileBrowserAdapter(this);
    mObserver = new FileListObserver();
    mAdapter.registerDataSetObserver(mObserver);
    // mConfiguration = ((BaseApplication) getApplication()).getInterpreterConfiguration();
    mManager = (SearchManager) getSystemService(Context.SEARCH_SERVICE);

    registerForContextMenu(getListView());
    updateAndFilterScriptList(mQuery);
    setListAdapter(mAdapter);
    handleIntent(getIntent());
  }

  @Override
  protected void onNewIntent(Intent intent) {
    handleIntent(intent);
  }

  @SuppressWarnings("serial")
  private void updateAndFilterScriptList(final String query) {
    List<File> scripts;
    File[] files = mCurrentDir.listFiles();
    if (files == null) {
      mCurrentDir = mBaseDir;
      files = mCurrentDir.listFiles();
    }
    setTitle(mCurrentDir.getPath());
    scripts = Arrays.asList(files);
    Predicate<File> p = new Predicate<File>() {

      @Override
      public boolean apply(File file) {
        return file.getName().toLowerCase().contains(query.toLowerCase());
      }
    };

    mScripts = Lists.newArrayList(Collections2.filter(scripts, p));

    synchronized (mQuery) {
      if (!mQuery.equals(query)) {
        if (query == null || query.equals(EMPTY)) {
          ((TextView) findViewById(R.id.left_text)).setText("Scripts");
        } else {
          ((TextView) findViewById(R.id.left_text)).setText(query);
        }
        mQuery = query;
      }
    }

    if (mScripts.size() == 0) {
      setEmpty("No matches found.");
    }
    mScripts.add(0, new File(mCurrentDir.getParent()) {
      @Override
      public boolean isDirectory() {
        return true;
      }

      @Override
      public String getName() {
        return "..";
      }
    });
  }

  private void handleIntent(Intent intent) {
    if (Intent.ACTION_SEARCH.equals(intent.getAction())) {
      mInSearchResultMode = true;
      String query = intent.getStringExtra(SearchManager.QUERY);
      updateAndFilterScriptList(query);
      mAdapter.notifyDataSetChanged();
    }
  }

  @Override
  public void onCreateContextMenu(ContextMenu menu, View v, ContextMenuInfo menuInfo) {
    menu.add(Menu.NONE, MenuId.RENAME.getId(), Menu.NONE, "Rename");
    menu.add(Menu.NONE, MenuId.DELETE.getId(), Menu.NONE, "Delete");
  }

  @Override
  public boolean onContextItemSelected(MenuItem item) {
    AdapterView.AdapterContextMenuInfo info;
    try {
      info = (AdapterView.AdapterContextMenuInfo) item.getMenuInfo();
    } catch (ClassCastException e) {
      Log.e("Bad menuInfo", e);
      return false;
    }
    File file = (File) mAdapter.getItem(info.position);
    int itemId = item.getItemId();
    if (itemId == MenuId.DELETE.getId()) {
      delete(file);
      return true;
    } else if (itemId == MenuId.RENAME.getId()) {
      rename(file);
      return true;
    }
    return false;
  }

  @Override
  public boolean onKeyDown(int keyCode, KeyEvent event) {
    if (keyCode == KeyEvent.KEYCODE_BACK) {
      if (mInSearchResultMode) {
        mInSearchResultMode = false;
        mAdapter.notifyDataSetInvalidated();
      } else {
        Intent intent = new Intent(this, PythonMain.class);
        intent.setAction(Intent.ACTION_MAIN);
        startActivity(intent);
      }
      return true;
    }
    return super.onKeyDown(keyCode, event);
  }

  private void setEmpty(String msg) {
    TextView v = (TextView) findViewById(android.R.id.empty);
    if (v != null) {
      v.setText(msg);
    }
  }

  @Override
  protected void onResume() {
    super.onResume();
    if (!mInSearchResultMode) {
      setEmpty("No Files");
    }
    updateAndFilterScriptList(mQuery);
    mAdapter.notifyDataSetChanged();
  }

  @Override
  public boolean onPrepareOptionsMenu(Menu menu) {
    super.onPrepareOptionsMenu(menu);
    menu.clear();
    menu.add(Menu.NONE, MenuId.SEARCH.getId(), Menu.NONE, "Search").setIcon(
        android.R.drawable.ic_menu_search);
    menu.add(Menu.NONE, MenuId.REFRESH.getId(), Menu.NONE, "Refresh").setIcon(
        android.R.drawable.ic_menu_revert);
    menu.add(Menu.NONE, MenuId.PLACES.getId(), Menu.NONE, "Places").setIcon(
        android.R.drawable.ic_menu_gallery);
    return true;
  }

  @Override
  public boolean onOptionsItemSelected(MenuItem item) {
    int itemId = item.getItemId();
    if (itemId == MenuId.REFRESH.getId()) {
      updateAndFilterScriptList(mQuery);
      mAdapter.notifyDataSetChanged();
    } else if (itemId == MenuId.SEARCH.getId()) {
      onSearchRequested();
    } else if (itemId == MenuId.PLACES.getId()) {
      doGetPlaces();
    }
    return true;
  }

  private void doGetPlaces() {
    AlertDialog.Builder builder = new AlertDialog.Builder(this);
    final CharSequence[] placesList = { "Main Files", "Extras", "Cache", "Scripts" };
    builder.setTitle("Places");
    builder.setItems(placesList, new DialogInterface.OnClickListener() {

      @Override
      public void onClick(DialogInterface dialog, int which) {
        PythonDescriptor descriptor = new PythonDescriptor();
        switch (which) {
        case 0:
          mBaseDir = getFilesDir();
          break;
        case 1:
          mBaseDir = new File(descriptor.getExtras());
          break;
        case 2:
          mBaseDir = getCacheDir();
          break;
        case 3:
          mBaseDir = new File(InterpreterConstants.SCRIPTS_ROOT);
          break;
        }
        mCurrentDir = mBaseDir;
        mAdapter.notifyDataSetInvalidated();
      }
    });
    builder.show();
  }

  @Override
  protected void onListItemClick(ListView list, View view, int position, long id) {
    final File file = (File) list.getItemAtPosition(position);
    mCurrent = file;
    if (file.isDirectory()) {
      mCurrentDir = file;
      mAdapter.notifyDataSetInvalidated();
      return;
    }
    doDialogMenu();
  }

  protected void showMessage(String message) {
    AlertDialog.Builder builder = new AlertDialog.Builder(this);
    builder.setTitle("Py4a File Browser");
    builder.setMessage(message);
    builder.setNeutralButton("OK", null);
    builder.show();
  }

  private void doDialogMenu() {
    AlertDialog.Builder builder = new AlertDialog.Builder(this);
    final CharSequence[] menuList = { "View", "Delete", "Rename" };
    builder.setTitle(mCurrent.getName());
    builder.setItems(menuList, new DialogInterface.OnClickListener() {

      @Override
      public void onClick(DialogInterface dialog, int which) {
        Intent intent;
        Uri uri;
        switch (which) {
        case 0:
          intent = new Intent(Intent.ACTION_VIEW);
          uri = Uri.fromFile(mCurrent);
          String mime = URLConnection.guessContentTypeFromName(uri.toString());
          if (mime == null) {
            String name = mCurrent.getName();
            if (name.endsWith(".html")) {
              mime = "text/html";
            } else {
              mime = "text/plain";
            }
          }
          intent.setDataAndType(uri, mime);
          try {
            startActivity(intent);
          } catch (Exception e) {
            showMessage(e.getMessage());
          }
          break;
        case 1:
          delete(mCurrent);
          break;
        case 2:
          rename(mCurrent);
          break;

        }
      }
    });
    builder.show();
  }

  /**
   * Opens the script for editing.
   * 
   * @param script
   *          the name of the script to edit
   */
  private void editScript(File script) {
    Intent i = new Intent(Constants.ACTION_EDIT_SCRIPT);
    i.putExtra(Constants.EXTRA_SCRIPT_PATH, script.getAbsolutePath());
    startActivity(i);
  }

  private void delete(final File file) {
    AlertDialog.Builder alert = new AlertDialog.Builder(this);
    alert.setTitle("Delete");
    alert.setMessage("Would you like to delete " + file.getName() + "?");
    alert.setPositiveButton("Yes", new DialogInterface.OnClickListener() {
      public void onClick(DialogInterface dialog, int whichButton) {
        FileUtils.delete(file);
        mScripts.remove(file);
        mAdapter.notifyDataSetChanged();
      }
    });
    alert.setNegativeButton("No", new DialogInterface.OnClickListener() {
      public void onClick(DialogInterface dialog, int whichButton) {
        // Ignore.
      }
    });
    alert.show();
  }

  private void addFolder() {
    final EditText folderName = new EditText(this);
    folderName.setHint("Folder Name");
    AlertDialog.Builder alert = new AlertDialog.Builder(this);
    alert.setTitle("Add Folder");
    alert.setView(folderName);
    alert.setPositiveButton("Ok", new DialogInterface.OnClickListener() {
      public void onClick(DialogInterface dialog, int whichButton) {
        String name = folderName.getText().toString();
        if (name.length() == 0) {
          Log.e(FileBrowser.this, "Folder name is empty.");
          return;
        } else {
          for (File f : mScripts) {
            if (f.getName().equals(name)) {
              Log.e(FileBrowser.this, String.format("Folder \"%s\" already exists.", name));
              return;
            }
          }
        }
        File dir = new File(mCurrentDir, name);
        if (!FileUtils.makeDirectories(dir, 0755)) {
          Log.e(FileBrowser.this, String.format("Cannot create folder \"%s\".", name));
        }
        mAdapter.notifyDataSetInvalidated();
      }
    });
    alert.show();
  }

  private void rename(final File file) {
    final EditText newName = new EditText(this);
    newName.setText(file.getName());
    AlertDialog.Builder alert = new AlertDialog.Builder(this);
    alert.setTitle("Rename");
    alert.setView(newName);
    alert.setPositiveButton("Ok", new DialogInterface.OnClickListener() {
      public void onClick(DialogInterface dialog, int whichButton) {
        String name = newName.getText().toString();
        if (name.length() == 0) {
          Log.e(FileBrowser.this, "Name is empty.");
          return;
        } else {
          for (File f : mScripts) {
            if (f.getName().equals(name)) {
              Log.e(FileBrowser.this, String.format("\"%s\" already exists.", name));
              return;
            }
          }
        }
        if (!FileUtils.rename(file, name)) {
          throw new RuntimeException(String.format("Cannot rename \"%s\".", file.getPath()));
        }
        mAdapter.notifyDataSetInvalidated();
      }
    });
    alert.show();
  }

  @Override
  public void onDestroy() {
    super.onDestroy();
    mManager.setOnCancelListener(null);
  }

  private class ScriptListObserver extends DataSetObserver implements ConfigurationObserver {
    @Override
    public void onInvalidated() {
      updateAndFilterScriptList(EMPTY);
    }

    @Override
    public void onConfigurationChanged() {
      runOnUiThread(new Runnable() {
        @Override
        public void run() {
          updateAndFilterScriptList(mQuery);
          mAdapter.notifyDataSetChanged();
        }
      });
    }
  }

  private abstract class FileListAdapter extends BaseAdapter {

    protected final Context mContext;
    protected final LayoutInflater mInflater;

    public FileListAdapter(Context context) {
      mContext = context;
      mInflater = (LayoutInflater) mContext.getSystemService(Context.LAYOUT_INFLATER_SERVICE);
    }

    @Override
    public int getCount() {
      return getScriptList().size();
    }

    @Override
    public Object getItem(int position) {
      return getScriptList().get(position);
    }

    @Override
    public long getItemId(int position) {
      return position;
    }

    private String permRwx(int perm) {
      String result;
      result =
          ((perm & 01) != 0 ? "r" : "-") + ((perm & 02) != 0 ? "w" : "-")
              + ((perm & 01) != 0 ? "x" : "-");
      return result;
    }

    private String permFileType(int perm) {
      String result = "?";
      switch (perm & S_IFMT) {
      case S_IFLNK:
        result = "s";
        break; /* symbolic link */
      case S_IFREG:
        result = "-";
        break; /* regular */
      case S_IFBLK:
        result = "b";
        break; /* block special */
      case S_IFDIR:
        result = "d";
        break; /* directory */
      case S_IFCHR:
        result = "c";
        break; /* character special */
      case S_IFIFO:
        result = "p";
        break; /* this is a FIFO */
      }
      return result;
    }

    public String permString(int perms) {
      String result;
      result = permFileType(perms) + permRwx(perms >> 6) + permRwx(perms >> 3) + permRwx(perms);
      return result;
    }

    public View getView(int position, View convertView, ViewGroup parent) {
      LinearLayout container;
      File script = getScriptList().get(position);

      if (convertView == null) {
        container = (LinearLayout) mInflater.inflate(R.layout.list_item, null);
      } else {
        container = (LinearLayout) convertView;
      }

      ImageView icon = (ImageView) container.findViewById(R.id.list_item_icon);
      int resourceId;
      if (script.isDirectory()) {
        resourceId = R.drawable.folder;
      } else {
        resourceId = R.drawable.sl4a_logo_32;
      }
      icon.setImageResource(resourceId);

      TextView text = (TextView) container.findViewById(R.id.list_item_title);

      String perms;
      try {
        perms = permString(FileUtils.getPermissions(script));
      } catch (Exception e) {
        perms = "????";
      }
      text.setText(getScriptList().get(position).getName() + " " + perms);
      return container;
    }

    protected abstract List<File> getScriptList();
  }

  private class FileBrowserAdapter extends FileListAdapter {
    public FileBrowserAdapter(Context context) {
      super(context);
    }

    @Override
    protected List<File> getScriptList() {
      return mScripts;
    }
  }

  private class FileListObserver extends DataSetObserver {
    @Override
    public void onInvalidated() {
      updateAndFilterScriptList(EMPTY);
    }
  }
}
