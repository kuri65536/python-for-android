* [Report issue](../README.md#create_issue)

Examples and Snippets
===

This page shows some Py4A snippets and examples.

Simple Example
---
* tested/in release

```python
import android

droid = android.Android()
droid.makeToast("Hello, Android!")

print("Hello World!")
```

Reading Phone State
---
* tested
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

Video phonecall (skype)
---
* 
need Skype app.

```python
import android

username = "user to call"
droid = android.Android()
i = droid.makeIntent("android.intent.action.VIEW", "skype://" + username)
droid.startActivityIntent(i)
```

<!---
 vi: ft=markdown:et:ts=4:fdm=marker
 -->
