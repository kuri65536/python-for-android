* [Report issue](../README.md#create_issue)

Examples and Snippets
===

This page shows some Py4A snippets and examples.

Simple Example
---
```python
import android

droid = android.Android()
droid.makeToast("Hello, Android!")

print("Hello World!")
```

Reading Phone State
---
eventWait() will block until an event occurs or an (optional) timeout (in ms) is exceeded.

```python
import android

droid = android.Android()
droid.startTrackingPhoneState()
try:
    print(droid.eventWait(2000))
finally:
    droid.stopTrackingPhoneState()
```

<!---
 vi: ft=markdown:et:ts=4:fdm=marker
 -->
