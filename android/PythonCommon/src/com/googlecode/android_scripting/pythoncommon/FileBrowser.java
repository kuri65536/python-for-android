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

package com.googlecode.android_scripting.pythoncommon;

import android.app.AlertDialog;
import android.app.Dialog;
import android.app.ListActivity;
import android.app.SearchManager;
import android.content.Context;
import android.content.DialogInterface;
import android.content.Intent;
import android.content.SharedPreferences;
import android.content.SharedPreferences.OnSharedPreferenceChangeListener;
import android.content.pm.PackageManager;
import android.content.pm.ResolveInfo;
import android.database.DataSetObserver;
import android.net.Uri;
import android.os.Bundle;
import android.preference.PreferenceManager;
import android.view.ContextMenu;
import android.view.ContextMenu.ContextMenuInfo;
import android.view.KeyEvent;
import android.view.LayoutInflater;
import android.view.Menu;
import android.view.MenuItem;
import android.view.View;
import android.view.ViewGroup;
import android.widget.AdapterView;
import android.widget.BaseAdapter;
import android.widget.CheckBox;
import android.widget.EditText;
import android.widget.ImageView;
import android.widget.LinearLayout;
import android.widget.ListView;
import android.widget.TextView;
import android.widget.Toast;

import com.googlecode.android_scripting.FileUtils;
import com.googlecode.android_scripting.FileUtils.FileStatus;
import com.googlecode.android_scripting.Log;
import com.googlecode.android_scripting.interpreter.InterpreterConstants;

import java.io.BufferedInputStream;
import java.io.BufferedOutputStream;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.InputStream;
import java.io.OutputStream;
import java.net.URLConnection;
import java.util.Arrays;
import java.util.Date;
import java.util.List;
import java.util.Vector;
import java.util.prefs.Preferences;

/**
 * Manages creation, deletion, and execution of stored scripts.
 * 
 * @author Damon Kohler (damonkohler@gmail.com)
 */
public class FileBrowser extends ListActivity implements OnSharedPreferenceChangeListener {

  private final static String EMPTY = "";

  private List<File> mScripts;
  private FileBrowserAdapter mAdapter;
  private FileListObserver mObserver;
  private SearchManager mManager;
  private boolean mInSearchResultMode = false;
  private String mQuery = EMPTY;
  private File mCurrentDir;
  private File mLastGoodDir;
  private File mBaseDir;
  private File mCurrent;
  private SharedPreferences mPreferences;
  private boolean mShowPermissions;
  private boolean mShowOwner;
  private boolean mShowSize;
  private PackageManager mPackageManager;

  private boolean mCut;
  private File mClipboard;
  private Dialog mPermissionDialog;

  // Linux stat constants
  public static final int S_IFMT = 0170000; /* type of file */
  public static final int S_IFLNK = 0120000; /* symbolic link */
  public static final int S_IFREG = 0100000; /* regular */
  public static final int S_IFBLK = 0060000; /* block special */
  public static final int S_IFDIR = 0040000; /* directory */
  public static final int S_IFCHR = 0020000; /* character special */
  public static final int S_IFIFO = 0010000; /* this is a FIFO */
  public static final int S_ISUID = 0004000; /* set user id on execution */
  public static final int S_ISGID = 0002000; /* set group id on execution */

  private static enum MenuId {
    DELETE, HELP, FOLDER_ADD, REFRESH, SEARCH, RENAME, COPY, CUT, PASTE, PLACES, PREFERENCES, MAIN,
    PERMISSIONS;
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
    mPreferences = PreferenceManager.getDefaultSharedPreferences(this);
    mPreferences.registerOnSharedPreferenceChangeListener(this);
    mPackageManager = getPackageManager();
    loadPreferences();
    registerForContextMenu(getListView());
    updateAndFilterScriptList(mQuery);
    setListAdapter(mAdapter);
    handleIntent(getIntent());
    mPermissionDialog = new Dialog(this);
    mPermissionDialog.setContentView(R.layout.permissions);
    mPermissionDialog.findViewById(R.id.btnOk).setOnClickListener(new View.OnClickListener() {
      @Override
      public void onClick(View v) {
        setPermissions();
      }
    });
    mPermissionDialog.findViewById(R.id.btnCancel).setOnClickListener(new View.OnClickListener() {
      @Override
      public void onClick(View v) {
        mPermissionDialog.hide();
      }
    });

  }

  private void loadPreferences() {
    mShowOwner = mPreferences.getBoolean("showOwner", false);
    mShowPermissions = mPreferences.getBoolean("showPermissions", true);
    mShowSize = mPreferences.getBoolean("showSize", false);
  }

  @Override
  protected void onNewIntent(Intent intent) {
    handleIntent(intent);
  }

  @SuppressWarnings("serial")
  private void updateAndFilterScriptList(final String query) {
    List<File> scripts;
    List<File> work;
    File[] files = mCurrentDir.listFiles();
    if (files == null) {
      showMessage("Access denied.");
      mCurrentDir = (mLastGoodDir != null) ? mLastGoodDir : mBaseDir;
      files = mCurrentDir.listFiles();
    }
    setTitle(mCurrentDir.getPath());
    scripts = Arrays.asList(files);

    work = new Vector<File>(scripts.size());
    for (File file : scripts) {
      if (query == null || query.equals(EMPTY)) {
        work.add(file);
      } else if (file.getName().toLowerCase().contains(query.toLowerCase())) {
        work.add(file);
      }
    }
    mScripts = work;

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
    File parent = mCurrentDir.getParentFile();
    if (parent != null) {
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
    mLastGoodDir = mCurrentDir;
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
    menu.add(Menu.NONE, MenuId.COPY.getId(), Menu.NONE, "Copy");
    menu.add(Menu.NONE, MenuId.CUT.getId(), Menu.NONE, "Cut");
    menu.add(Menu.NONE, MenuId.PASTE.getId(), Menu.NONE, "Paste");
    menu.add(Menu.NONE, MenuId.PERMISSIONS.getId(), Menu.NONE, "Permissions");
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
    } else if (itemId == MenuId.COPY.getId()) {
      addCopy(mCurrent);
    } else if (itemId == MenuId.CUT.getId()) {
      addCut(mCurrent);
    } else if (itemId == MenuId.PASTE.getId()) {
      pasteFile();
    } else if (itemId == MenuId.PERMISSIONS.getId()) {
      showPermissions();
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
        if (mScripts != null && mScripts.size() > 0) {
          File first = mScripts.get(0);
          if (first.getName().equals("..")) {
            mCurrentDir = first;
            mAdapter.notifyDataSetInvalidated();
            return true;
          }
        }
        doGotoMain();
        return true;
      }
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
    menu.add(Menu.NONE, MenuId.PREFERENCES.getId(), Menu.NONE, "Preferences").setIcon(
        android.R.drawable.ic_menu_preferences);
    menu.add(Menu.NONE, MenuId.MAIN.getId(), Menu.NONE, "Main").setIcon(
        android.R.drawable.ic_menu_manage);
    menu.add(Menu.NONE, MenuId.FOLDER_ADD.getId(), Menu.NONE, "Add Folder").setIcon(
        android.R.drawable.ic_menu_add);
    if (mClipboard != null) {
      menu.add(Menu.NONE, MenuId.PASTE.getId(), Menu.NONE, "Paste");
    }
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
    } else if (itemId == MenuId.PREFERENCES.getId()) {
      startActivity(new Intent(this, Preferences.class));
    } else if (itemId == MenuId.MAIN.getId()) {
      doGotoMain();
    } else if (itemId == MenuId.FOLDER_ADD.getId()) {
      addFolder();
    } else if (itemId == MenuId.PASTE.getId()) {
      pasteFile();
    }
    return true;
  }

  private void doDialogMenu() {
    AlertDialog.Builder builder = new AlertDialog.Builder(this);
    final CharSequence[] menuList = { "View", "Delete", "Rename", "Copy", "Cut", "Permissions" };
    builder.setTitle(mCurrent.getName());
    builder.setItems(menuList, new DialogInterface.OnClickListener() {

      @Override
      public void onClick(DialogInterface dialog, int which) {
        switch (which) {
        case 0:
          doViewCurrent();
          break;
        case 1:
          delete(mCurrent);
          break;
        case 2:
          rename(mCurrent);
          break;
        case 3:
          addCopy(mCurrent);
          break;
        case 4:
          addCut(mCurrent);
          break;
        case 5:
          showPermissions();
        }
      }
    });
    builder.show();
  }

  /**
   * Go to current packages main activity.
   */
  public void doGotoMain() {
    Intent intent = new Intent(Intent.ACTION_MAIN); // Should default to main screen.
    String packageName = getPackageName();
    intent.setPackage(packageName);
    intent.addCategory(Intent.CATEGORY_LAUNCHER);
    ResolveInfo r = mPackageManager.resolveActivity(intent, 0);
    intent.setClassName(packageName, r.activityInfo.name);
    try {
      startActivity(intent);
    } catch (Exception e) {
      showMessage(e.getMessage());
    }
  }

  private void setPermBit(int perms, int bit, int id) {
    CheckBox ck = (CheckBox) mPermissionDialog.findViewById(id);
    ck.setChecked(((perms >> bit) & 1) == 1);
  }

  private int getPermBit(int bit, int id) {
    CheckBox ck = (CheckBox) mPermissionDialog.findViewById(id);
    int ret = (ck.isChecked()) ? (1 << bit) : 0;
    return ret;
  }

  /**
   * Show and edit file permissions
   */
  public void showPermissions() {
    mPermissionDialog.setTitle(mCurrent.getName());
    try {
      int perms = FileUtils.getPermissions(mCurrent);
      setPermBit(perms, 8, R.id.ckOwnRead);
      setPermBit(perms, 7, R.id.ckOwnWrite);
      setPermBit(perms, 6, R.id.ckOwnExec);
      setPermBit(perms, 5, R.id.ckGrpRead);
      setPermBit(perms, 4, R.id.ckGrpWrite);
      setPermBit(perms, 3, R.id.ckGrpExec);
      setPermBit(perms, 2, R.id.ckOthRead);
      setPermBit(perms, 1, R.id.ckOthWrite);
      setPermBit(perms, 0, R.id.ckOthExec);
      TextView v = (TextView) mPermissionDialog.findViewById(R.id.permInfo);
      Date date = new Date(mCurrent.lastModified());
      v.setText(mCurrent.getParent() + "\nSize=" + mCurrent.length() + "\nModified=" + date);
      mPermissionDialog.show();
    } catch (Exception e) {
      showMessage(e.getMessage());
    }
  }

  /**
   * Perform permission setting
   */
  public void setPermissions() {
    mPermissionDialog.hide();
    int perms =
        getPermBit(8, R.id.ckOwnRead) | getPermBit(7, R.id.ckOwnWrite)
            | getPermBit(6, R.id.ckOwnExec) | getPermBit(5, R.id.ckGrpRead)
            | getPermBit(4, R.id.ckGrpWrite) | getPermBit(3, R.id.ckGrpExec)
            | getPermBit(2, R.id.ckOthRead) | getPermBit(1, R.id.ckOthWrite)
            | getPermBit(0, R.id.ckOthExec);

    try {
      FileUtils.chmod(mCurrent, perms);
      toast(Integer.toString(perms, 8));
      mAdapter.notifyDataSetChanged();
    } catch (Exception e) {
      showMessage(e.getMessage());
    }
  }

  /**
   * Attempt to view or edit the current file. Assume text unless told otherwise.
   */
  private void doViewCurrent() {
    Intent intent = new Intent(Intent.ACTION_VIEW);
    Uri uri = Uri.fromFile(mCurrent);
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
  }

  public void toast(String message) {
    Toast.makeText(this, message, Toast.LENGTH_SHORT).show();
  }

  private void addCopy(File file) {
    mClipboard = file;
    toast("Copy to clipboard\n" + file.getName());
    mCut = false;
  }

  private void addCut(File file) {
    mClipboard = file;
    toast("Cut to clipboard\n" + file.getName());
    mCut = true;
  }

  private void pasteFile() {
    String message = "";
    if (mClipboard == null) {
      showMessage("Nothing to copy");
      return;
    }
    final File destination = new File(mCurrentDir, mClipboard.getName());
    if (destination.exists()) {
      message = "File " + destination.getName() + " already exists. Overwrite?";
    }
    if (message != "") {
      prompt(message, new DialogInterface.OnClickListener() {

        @Override
        public void onClick(DialogInterface dialog, int which) {
          if (which == AlertDialog.BUTTON_POSITIVE) {
            performPasteFile(mClipboard, destination);
          }
        }
      });
    } else {
      performPasteFile(mClipboard, destination);
    }

  }

  protected void performPasteFile(File source, File destination) {
    if (source.isDirectory()) {
      showMessage("Haven't worked out folder copy yet...");
    } else {
      try {
        copyFile(source, destination);
        if (mCut) {
          source.delete();
        }
        mClipboard = null;
        showMessage("Copied.");
      } catch (Exception e) {
        showMessage(e.getMessage());
      }
      mAdapter.notifyDataSetInvalidated();
    }
  }

  /**
   * Copy file from source to destination.
   * 
   * @param source
   * @param destination
   */

  private void copyFile(File source, File destination) throws Exception {
    byte[] buf = new byte[1024];
    InputStream input = new BufferedInputStream(new FileInputStream(source));
    OutputStream output = new BufferedOutputStream(new FileOutputStream(destination));
    int len;
    while ((len = input.read(buf)) > 0) {
      output.write(buf, 0, len);
    }
    output.flush();
    output.close();
    int perms = FileUtils.getPermissions(source) & 0777;
    FileUtils.chmod(destination, perms);
    destination.setLastModified(source.lastModified());
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

  protected void prompt(String message, DialogInterface.OnClickListener btnlisten) {
    AlertDialog.Builder builder = new AlertDialog.Builder(this);
    builder.setTitle("File Browser");
    builder.setMessage(message);
    builder.setNegativeButton("Cancel", btnlisten);
    builder.setPositiveButton("OK", btnlisten);
    builder.show();
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
          ((perm & 04) != 0 ? "r" : "-") + ((perm & 02) != 0 ? "w" : "-")
              + ((perm & 1) != 0 ? "x" : "-");
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
      String line = script.getName();
      if (mShowPermissions) {
        try {
          perms = permString(FileUtils.getPermissions(script));
        } catch (Exception e) {
          perms = "????";
        }
        line += " " + perms;
      }
      if (mShowSize) {
        line += " " + script.length();
      }
      if (mShowOwner) {
        String owner = "";
        try {
          FileStatus fs = FileUtils.getFileStatus(script);
          if (fs.uid != 0) {
            owner = mPackageManager.getNameForUid(fs.uid);
          }
        } catch (Exception e) {
          owner = "?";
        }
        line += " " + owner;
      }

      text.setText(line);
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

  @Override
  public void onSharedPreferenceChanged(SharedPreferences sharedPreferences, String key) {
    loadPreferences();
    mAdapter.notifyDataSetInvalidated();
  }
}
