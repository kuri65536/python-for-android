* [Report issue](../README.md#create_issue)

Tips: Helper Files
---
[androidhelper.py](https://github.com/kuri65536/python-for-android/tree/master/tools/androidhelper.py)
for simplifying Python-for-Android SL4A development in IDEs.

This creates a "helper" class derived from the default Android class
and defines [SL4A](https://github.com/kuri65536/sl4a)
functions with API documentation in DocString & uses RPC calls derived
from the base android.py.

Details
---
You can import this file into your scripts in your IDE to use Autocompletion, Documentation popups
etc.

To Use: replace the standard `import android` line with
```python
try:
  import androidhelper as android
except:
  import android
```

This will pull the helper class in if it is available, and fall through to the default android
class if not.


Generating
---
To generate this file, I have written
[createandroidhelper.py](https://github.com/kuri65536/python-for-android/tree/master/tools/createandroidhelper.py).

After some trial & error, I finally chose to use the HTML documentation
contained at
https://github.com/kuri65536/sl4a/tree/master/android/ScriptingLayerForAndroid/assets/sl4adoc.zip
to generate androidhelper.py.

Note that this currently has issues with 2 API functions which need manual
corrections in androidhelper.py - both documented in the file comments.
<!---
 vi: ft=markdown:et:ts=4:fdm=marker
 -->
