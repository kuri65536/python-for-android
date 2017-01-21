# Copyright (C) 2017 shimoda kuri65536@hotmail.com
# Copyright (C) 2009 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not
# use this file except in compliance with the License. You may obtain a copy of
# the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations under
# the License.
from __future__ import print_function

__author__ = 'Damon Kohler <damonkohler@gmail.com>'

import time
import collections
import json
import os
import socket
from logging import warning as warn

PORT = os.environ.get('AP_PORT')
HOST = os.environ.get('AP_HOST')
HANDSHAKE = os.environ.get('AP_HANDSHAKE')
Result = collections.namedtuple('Result', 'id,result,error')


class Android(object):

  def __init__(self, addr=None):
    if addr is None:
      addr = HOST, PORT

    if True:
        try:
            self.conn = socket.create_connection(addr)
        except:
            self.conn = self.launchSL4A(addr)

    self.client = self.conn.makefile('rw', encoding='utf-8')
    self.id = 0
    if HANDSHAKE is not None:
      self._authenticate(HANDSHAKE)

  def _rpc(self, method, *args):
    data = {'id': self.id,
            'method': method,
            'params': args}
    request = json.dumps(data)
    self.client.write(request+'\n')
    self.client.flush()
    response = self.client.readline()
    self.id += 1
    result = json.loads(response)
    if result['error'] is not None:
      print(result['error'])
    # namedtuple doesn't work with unicode keys.
    return Result(id=result['id'], result=result['result'],
                  error=result['error'], )

  def __getattr__(self, name):
    def rpc_call(*args):
      return self._rpc(name, *args)
    return rpc_call

  if True:
    def launchSL4A(self, addr):
        if addr[0] is None:
            addr = ("127.0.0.1", addr[1])
        if addr[1] is None:
            addr = (addr[0], "8888")
        sl4a = 'com.googlecode.android_scripting'
        cmd = ('am start -a %s.action.LAUNCH_SERVER '
               '--ei %s.extra.USE_SERVICE_PORT %s '
               '%s/.activity.ScriptingLayerServiceLauncher '
               % (sl4a, sl4a, addr[1], sl4a))
        warn("launch SL4A with %s" % str(addr))
        os.system(cmd)
        time.sleep(2)
        return socket.create_connection(addr)

# vi: et:ts=4:nowrap
