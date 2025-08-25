##############################################################################
#
# Copyright (c) 2023 Nexedi SA and Contributors. All Rights Reserved.
#                     Rafael Monnerat <rafael@nexedi.com>
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################

from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from Products.ERP5Type.tests.utils import parseListeningAddress

from six import BytesIO
import socket
import time
import os
import shutil
import contextlib
import multiprocessing
import requests
import tarfile
from random import randint

import caucase.cli
import caucase.http

def canConnect(caucase_url):
  """
  Returns True if a connection can be established to given address, False
  otherwise.
  """
  try:
    requests.get(caucase_url)
  except BaseException:
    return False
  return True

def findFreeTCPPortRange(ip='', count=1):
  # type: (str, int) -> int
  """Find a range of consecutive `count` free TCP ports to listen to.
  """
  for _ in range(10):  # retry 10 times
    port = random.randrange(20000, 30000)
    for offset in range(count):
      with closing(socket.socket(
          socket.AF_INET6 if ':' in ip else socket.AF_INET, socket.SOCK_STREAM)) as s:
        try:
          s.bind((ip, port + offset))
        except OSError:
          port = None
          break
  if port is None:
    raise RuntimeError("Can't find port")
  return port

def retry(callback, try_count=10, try_delay=0.1):
    """
    Poll <callback> every <try_delay> for <try_count> times or until it returns
    a true value.
    Always returns the value returned by latest callback invocation.
    """
    for _ in range(try_count):
      result = callback()
      if result:
        break
      time.sleep(try_delay)
    return result

class ERP5TypeCaucaseTestCase(ERP5TypeTestCase):
  """ Helpfull code to start/stop/control a caucased service for the tests
  """
  caucase_certificate_kw = {}
  def _startCaucaseServer(self, argv=(), timeout=10):
    """
    Start caucased server
    """
    zserver = os.environ.get("zserver")
    ip = "127.0.0.1"
    for _ip, _ in parseListeningAddress(zserver):
      if _ip is not None:
        ip = _ip
        break
    port = findFreeTCPPortRange(ip)
    self.caucase_runtime = caucase_runtime = multiprocessing.Process(
      target=caucase.http.main,
      kwargs=dict(
        argv=[
          '--db', self.caucase_db,
          '--server-key', os.path.join(self.caucased, 'server.key.pem'),
          '--netloc', '%s:%s' % (ip, port),
          '--service-auto-approve-count', '0'
        ]
      )
    )
    self.caucase_runtime.start()
    self.caucase_url = 'http://%s:%s' % (ip, port)

    if not caucase_runtime.is_alive():
      self._stopCaucaseServer()
      raise AssertionError('Something wrong happens because caucase didnt started')

    if not retry(
      lambda: (
        self.assertTrue(caucase_runtime.is_alive()) or
        canConnect(self.caucase_url)
      ),
      try_count=timeout * 10,
    ):
      self._stopCaucaseServer()
      raise AssertionError('Could not connect to %r after %i seconds' % (
        self.caucase_url,
        timeout,
      ))

  def _stopCaucaseServer(self):
    """
    Stop a running caucased server
    """
    self.caucase_runtime.terminate()
    self.caucase_runtime.join()
    if self.caucase_runtime.is_alive():
      raise ValueError('%r does not wish to die' % (self.caucase_runtime, ))

  def setUpCaucase(self):
    portal_web_service = getattr(self.portal, "portal_web_services", None)
    if portal_web_service is None:
      raise ValueError("Please install erp5_web_service before continue")

    testdir = os.path.join(os.environ['INSTANCE_HOME'],
                           self.__class__.__module__)

    self.caucased = os.path.join(testdir, 'caucased')
    self.caucase_db = os.path.join(self.caucased, 'caucase.sqlite')
    self.caucase_service = os.path.join(testdir, 'service')
    test_caucase_connector = getattr(portal_web_service, "test_caucase_connector", None)
    if test_caucase_connector is None:
      if os.path.exists(testdir):
        shutil.rmtree(testdir)
      os.mkdir(testdir)
      os.mkdir(self.caucased)
      os.mkdir(self.caucase_service)
      test_caucase_connector = portal_web_service.newContent(
        id="test_caucase_connector",
        portal_type="Caucase Connector",
        reference="erp5-certificate-login",
        user_key=None,
        user_certificate=None,
        **self.caucase_certificate_kw
      )
      test_caucase_connector.validate()

    try:
      self._startCaucaseServer()
    except AssertionError:
       # The server fail to start, probably another process 
       # running in parallel picked the port, so sleep a random
       # moment to increase the chance of success
       time.sleep(randint(1,3))
       self._startCaucaseServer()

    self.addCleanup(self._stopCaucaseServer)
    test_caucase_connector.setUrlString(self.caucase_url)
    test_caucase_connector.bootstrapCaucaseConfiguration()
    if not retry(
      lambda: (
        test_caucase_connector.hasUserCertificateRequestReference() or
        test_caucase_connector.getUserCertificate() is None
      ),
      try_count=100,
      try_delay=1
    ):
      raise ValueError("Unable to configure")

