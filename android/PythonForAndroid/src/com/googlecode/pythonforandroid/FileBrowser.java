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
import com.googlecode.android_scripting.interpreter.InterpreterConfiguration.ConfigurationObserver;

import java.io.File;
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

  private static enum MenuId {
    DELETE, HELP, FOLDER_ADD, REFRESH, SEARCH, RENAME, COPY;
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
    if (keyCode == KeyEvent.KEYCODE_BACK && mInSearchResultMode) {
      mInSearchResultMode = false;
      mAdapter.notifyDataSetInvalidated();
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
    }
    return true;
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

  private void doDialogMenu() {
    AlertDialog.Builder builder = new AlertDialog.Builder(this);
    final CharSequence[] menuList =
        { "Run Foreground", "Run Background", "Edit", "Delete", "Rename" };
    builder.setTitle(mCurrent.getName());
    builder.setItems(menuList, new DialogInterface.OnClickListener() {

      @Override
      public void onClick(DialogInterface dialog, int which) {
        switch (which) {
        case 3:
          delete(mCurrent);
          break;
        case 4:
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
        perms = Integer.toString(FileUtils.getPermissions(script), 8);
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
