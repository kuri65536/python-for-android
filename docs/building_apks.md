* [Report issue](../README.md#create_issue)

Buildin APK
===
You can mostly follow the instructions in the SL4A Wiki:

https://github.com/kuri65536/sl4a/tree/master/docs/SharingScripts.md

Python-specific Tricks
---
This is based on the SL4A project template,
and builds on the wiki page linked from above.

Adding pure Python modules as dependencies
---
You can't put folders into /res/raw/, so you have to zip up all the pure Python modules that your
script requires, and place the resulting .zip file into /res/raw/ (alongsite script.py). In
script.py, you have to add the following snippet before you import any of the dependencies:

```python
import sys
import os
sys.path.insert(1, os.path.join(os.path.dirname(__file__), 'modules.zip'))
```

<!---
 vi: ft=markdown
 -->
