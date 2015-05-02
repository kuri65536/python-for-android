# Examples and Snippets #

This page shows some Py4A snippets and examples.


### Simple Example ###
```
import android

droid = android.Android()
droid.makeToast("Hello, Android!")

print("Hello World!")
```

### Reading Phone State ###
eventWait() will block until an event occurs or an (optional) timeout (in ms) is exceeded.

```
import android

droid = android.Android()
droid.startTrackingPhoneState()
try:
  print(droid.eventWait(2000))
finally:
  droid.stopTrackingPhoneState()
```