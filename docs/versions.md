* [Report issue](../README.md#create_issue)

Feature request
===
## Modules
* Numpy -- compillation was succeed, but not work...
* Matplotlib -- GUI is not impossible with SL4A, but image generation can.
* Pillow #9 -- may be useful with webview or another python modules.
* IPython Notebook server #61
* [paramiko](https://github.com/paramiko/paramiko) #44
* PyGame #55 -- GUI is not impossible with SL4A

History
===

PythonForAndroid\_r25
---
* Python 2.7.9 => 2.7.10 (no patch modification is needed.)

PythonForAndroid\_r24
---

PythonForAndroid\_r23
---

PythonForAndroid\_r22
---
* disable to use symbolic link, this is not valid with android unzip.
* disable wchar from ctypes module. idea from [ML](https://groups.google.com/forum/?hl=en#!searchin/python-android/ctypes/python-android/vDaaJXNYz_A/eazMVI-DQSYJ)
* strip shared binary again.

PythonForAndroid\_r21
---
* openssl with armv5te for old devices.
* [compile SSL for armv5te](http://stackoverflow.com/questions/16810110/how-to-build-openssl-to-generate-libcrypto-a-with-android-ndk-and-windows)
* enable zlib for python3

  * [setup.py must be patched](http://code.activestate.com/lists/python-list/329410/)
  * use boinc zlib. (strange version 1.2.3, patch may not work in the far future.)

PythonForAndroid\_r20
---
* use run_pie.c for GB or ealier

PythonForAndroid\_r19
---
* python 2.7.8 => 2.7.9

PythonForAndroid\_r18
---
  * new: python3 => 3.4.3
  * openssl => 1.0.2a

PythonForAndroid\_r17
---
  * move the host from GoogleCode to GitHub
  * python => 2.7.8

PythonForAndroid\_r5
---
  * Should cope with shared libraries in installed modules better,
  * Will handle egg (and zip) files automatically.

PythonForAndroid\_r4
---
  * Fixed bug with module installer and empty files.

PythonForAndroid\_r3
---
  * Added egg support: Python modules can now be self contained into an egg file, so standard Python eggs can be installed easily.
  * Added modules removal: Along with Robbie's great Module installer
    I came up with a rough but still work Egg uninstaller,
    now you can install an egg module, the system will take care on
    installing each piece on the right place (scripts into sdcard and binary into /data)
    and then you'll be able to uninstall them.
  * Shows the latest available version for each piece: Now the main Python
    application (the one from where you install) let's you know which are
    the latest available versions for each of the needed parts by just going and ask our Google Code site.
  * Added `_struct module`
  * Improved binary module creation, now we provide with a system compatible
    with setuptools so egg files can be created by just calling
    python setup.py (after some slight patching of the setup.py script).
    See BuildingModules
  * Added Py4A Logo, thanks to Robbie for working on this, I suck for that.

This version is the first one signed with our official key, so you will
have to remove previous installations of Py4A.

<!---
 vi: ft=markdown:et:fdm=marker
 -->
