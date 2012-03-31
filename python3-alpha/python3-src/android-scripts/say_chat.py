__author__ = "Brian Lenihan <brian.lenihan@gmail.com"
__copyright__ = "Copyright (c) 2012 Python for Android Project"
__license__ = "Apache License, Version 2.0"

import logging
import android

from pyxmpp2.jid import JID
from pyxmpp2.client import Client
from pyxmpp2.settings import XMPPSettings
from pyxmpp2.interfaces import XMPPFeatureHandler
from pyxmpp2.interfaces import EventHandler, event_handler, QUIT
from pyxmpp2.interfaces import message_stanza_handler
from pyxmpp2.streamevents import DisconnectedEvent
from pyxmpp2.ext.version import VersionProvider

logging.basicConfig(level = logging.INFO)
xmpp_trace  = False

class SayChat(EventHandler, XMPPFeatureHandler):
  def __init__(self):
      self.droid = android.Android()
      settings = XMPPSettings({"software_name": "Say Chat"})
      settings["jid"] = self.droid.dialogGetInput("Google Talk Username").result
      settings["password"] = self.droid.dialogGetInput("Google Talk Password").result
      settings["server"] = "talk.google.com"
      settings["starttls"] = True
      self.client = Client(
        JID(settings["jid"]),
        [self, VersionProvider(settings)],
        settings)
      
  def connect(self):
    self.client.connect()
    self.client.run()

  def disconnect(self):
    self.client.disconnect()
    self.client.run(timeout = 2)

  @message_stanza_handler()
  def handle_message(self, stanza):
    self.droid.ttsSpeak(
      "{!s} says {!s}".format(stanza.from_jid.as_unicode(),
      stanza.body))
    return ""
    
  @event_handler(DisconnectedEvent)
  def handle_disconnected(self, event):
    return QUIT
    
  @event_handler()
  def handle_all(self, event):
    """If it's not logged, it didn't happen."""
    logging.info("-- {}".format(event))

  def run(self):
    try:
      self.connect()
    except KeyboardInterrupt:
      self.disconnect()

if xmpp_trace:
  handler = logging.StreamHandler()
  handler.setLevel(logging.DEBUG)
  for logger in ("pyxmpp2.IN", "pyxmpp2.OUT"):
    logger = logging.getLogger(logger)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(handler)
    logger.propagate = False

saychat = SayChat()
saychat.run()    
