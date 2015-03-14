# Introduction #

[androidhelper.py](http://code.google.com/p/python-for-android/downloads/detail?name=androidhelper.py) for simplifying Python-for-Android SL4A development in IDEs. This creates a "helper" class derived from the default Android class and defines SL4A [R5](https://code.google.com/p/python-for-android/source/detail?r=5) functions with API documentation in DocString & uses RPC calls derived from the base android.py.

# Details #

You can import this file into your scripts in your IDE to use Autocompletion, Documentation popups etc.

To Use: replace the standard `import android` line with
```
try:
  import androidhelper as android
except:
  import android
```

This will pull the helper class in if it is available, and fall through to the default android class if not.

## Generating ##
To generate this file, I have written [createandroidhelper.py](http://code.google.com/p/python-for-android/downloads/detail?name=createandroidhelper.py).

After some trial & error, I finally chose to use the HTML documentation contained at http://android-scripting.googlecode.com/hg/android/ScriptingLayerForAndroid/assets/sl4adoc.zip to generate androidhelper.py. Note that this currently has issues with 2 API functions which need manual corrections in androidhelper.py - both documented in the file comments.