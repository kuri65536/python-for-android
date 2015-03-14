# PythonForAndroid\_r5 #
  * Should cope with shared libraries in installed modules better,
  * Will handle egg (and zip) files automatically.
# PythonForAndroid\_r4 #
  * Fixed bug with module installer and empty files.
# PythonForAndroid\_r3 #
  * Added egg support: Python modules can now be self contained into an egg file, so standard Python eggs can be installed easily.
  * Added modules removal: Along with Robbie's great Module installer I came up with a rough but still work Egg uninstaller, now you can install an egg module, the system will take care on installing each piece on the right place (scripts into sdcard and binary into /data) and then you'll be able to uninstall them.
  * Shows the latest available version for each piece: Now the main Python application (the one from where you install) let's you know which are the latest available versions for each of the needed parts by just going and ask our Google Code site.
  * Added `_struct module`
  * Improved binary module creation, now we provide with a system compatible with setuptools so egg files can be created by just calling python setup.py (after some slight patching of the setup.py script). See BuildingModules
  * Added Py4A Logo, thanks to Robbie for working on this, I suck for that.

This version is the first one signed with our official key, so you will
have to remove previous installations of Py4A.