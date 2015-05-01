__author__ = "Brian Lenihan <brian.lenihan@gmail.com"
__copyright__ = "Copyright (c) 2012 Python for Android Project"
__license__ = "Apache License, Version 2.0"

import os
import logging
import android

"""
Create and set a new Tasker variable, display the variable's value in a Tasker
popup, and then clear the variable.

Misc / Allow External Access must be set in Tasker's prefs.

Tasker action code reference:
  http://tasker.dinglisch.net/ActionCodes.java
"""
SET_VARIABLE = 547
CLEAR_VARIABLE = 549
POPUP = 550

logging.basicConfig(level=logging.INFO)

class Tasker(object):
  def __init__(self):
    self.droid = android.Android()
    self.extras = dict(
      version_number = '1.0',
      task_name = 'tasker_demo.{}'.format(os.getpid()),
      task_priority = 9)
    self.actions = 0

  def bundle(self, action, *args):
    # Unused parameters are padded with False
    args = list(args)
    args.extend([False]*(6-len(args)))

    self.actions += 1
    self.extras.update(
      {'action{}'.format(self.actions) : dict(
        {'action' : action,
         'arg:1' : args[0],
         'arg:2' : args[1],
         'arg:3' : args[2],
         'arg:4' : args[3],
         'arg:5' : args[4],
         'arg:6' : args[5]})
         })

  def broadcast_intent(self):
    intent = self.droid.makeIntent(
      'net.dinglisch.android.tasker.ACTION_TASK', None, None, self.extras).result
    logging.debug("-- {}".format(intent))
    self.droid.sendBroadcastIntent(intent) 

if __name__ == "__main__":
  tasker = Tasker()
  tasker.bundle(SET_VARIABLE, "%PY4A_DEMO", "Hello from python")
  # Popup: String title, String text, String background image, Scene layout,
  # Integer timeout, Boolean show over keyguard, Boolean condition
  tasker.bundle(POPUP, "Tasker", "%PY4A_DEMO", "", "Popup", 5, True, False)
  tasker.bundle(CLEAR_VARIABLE, "%PY4A_DEMO")
  tasker.broadcast_intent()
