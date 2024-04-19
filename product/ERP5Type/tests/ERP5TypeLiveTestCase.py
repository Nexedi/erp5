# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2002-2010 Nexedi SA and Contributors. All Rights Reserved.
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsibility of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# guarantees and support are strongly adviced to contract a Free Software
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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
##############################################################################

import unittest
import os
import sys
import imp
import re
import warnings

from zope.component.hooks import setSite
from zope.globalrequest import getRequest
from Acquisition import aq_base
from Testing import ZopeTestCase
from Testing.ZopeTestCase import connections, PortalTestCase, user_name
from Products.CMFCore.utils import getToolByName
from Products.ERP5Type.tests.ProcessingNodeTestCase import ProcessingNodeTestCase
from Products.ERP5Type.tests.SecurityTestCase import SecurityTestCase
from Products.ERP5Type.tests.ERP5TypeTestCase import (
  ERP5TypeTestCase,
  ERP5TypeTestCaseMixin,
  ERP5TypeTestCaseRequestConnection,
  ERP5ReportTestCase,
)
from glob import glob
import transaction
import six
if not six.PY2:
  from importlib import reload

from zLOG import LOG, DEBUG, INFO

# Disable patching of activity tool,
# Tic doesn't need help as TimerService is running
from Products.ERP5Type.tests import ProcessingNodeTestCase as\
                                    ProcessingNodeTestCaseModule
ProcessingNodeTestCaseModule.patchActivityTool = lambda: None

_request_server_url = None

class ERP5TypeLiveTestCase(ERP5TypeTestCaseMixin):
    """ERP5TypeLiveTestCase is the default class for *all* tests
    in ERP5. It is designed with the idea in mind that tests should
    be run through the web. Command line based tests may be helpful
    sometimes but should remain an exception because they hinder
    productivity by adding an extra time to build the
    environment (which is already built in live instances).

    All other test classes should derive from ERP5TypeLiveTestCase.

    TODO:
    - An eplicit list of exceptions to live tests remains to be
      defined.
    """
    portal = None
    _added_property_sheets = {}

    def getPortalName(self):
      """ Return the default ERP5 site id.
      """
      return self.portal.getId()

    def getPortal(self):
      """Returns the portal object, i.e. the "fixture root".

      Rewrap the portal in an independent request for this test.
      """
      if self.portal is not None:
        return self.portal

      from Products.ERP5.ERP5Site import getSite
      site = getSite()
      # reconstruct the acquisition chain with an independent request.
      #   RequestContainer -> Application -> Site
      from Testing.makerequest import makerequest
      environ = {}
      if self._server_address:
        host, port = self._server_address
        environ={
          'SERVER_NAME': host,
          'SERVER_PORT': str(port),
        }
      portal = getattr(
        makerequest(aq_base(site.aq_parent), environ=environ),
        site.getId())

      request = portal.REQUEST
      if _request_server_url:
        request['SERVER_URL'] = _request_server_url
        request._resetURLS()
      self._request_connection = ERP5TypeTestCaseRequestConnection(request)
      connections.register(self._request_connection)

      portal.setupCurrentSkin(request)
      setSite(portal)
      self.portal = portal
      return portal

    getPortalObject = getPortal

    def createSimpleUser(self, title, reference, *args, **kwargs):
      """
      Convenient helper to avoid recreating user every time (in non-Live Test, data
      is not kept and usually these users are only created in setUpOnce() (not
      used in favor of afterSetUp() in Live Tests)
      """
      if not self.portal.acl_users.getUserById(reference):
        return super(ERP5TypeLiveTestCase,
                     self).createSimpleUser(title, reference, *args, **kwargs)

    def _close(self):
      '''Closes the ZODB connection.'''

      self.abort()
      self._restoreMailHost()
      if getattr(self, "activity_tool_subscribed", False):
        self.portal.portal_activities.subscribe()
        self.commit()
      if self.portal is not None:
        # With a live test, we don't close all connections, because the ZODB connection
        # was not opened by us. 
        self.portal.REQUEST.close()
        self.portal = None
        connections.close(self._request_connection)

    def _setup(self):
        '''Change some site properties in order to be ready for live test
        '''
        # force a random password for ERP5TypeTestCase user by removing
        # any existing one
        try:
          self.portal.acl_users.zodb_users.removeUser('ERP5TypeTestCase')
        except (AttributeError, KeyError):
          pass
        # Disabling portal_activities is required in order to avoid
        # conflict with other threads doing tic in the same time
        self.login()
        self.activity_tool_subscribed = self.getPortalObject()\
                .portal_activities.isSubscribed()
        self.portal.portal_activities.unsubscribe()
        self._setUpDummyMailHost()

    setUp = PortalTestCase.setUp

    def tearDown(self):
        self.doCleanups()
        PortalTestCase.tearDown(self)

    def _app(self):
        '''Returns the app object for a test.'''
        return self.getPortal().aq_parent

    def afterSetUp(self):
      '''Called after setUp() has completed. This is
         far and away the most useful hook.
      '''
      pass

    def publish(self, *args, **kw):
      from zope.security.management import endInteraction, restoreInteraction
      endInteraction()
      try:
        return super(ERP5TypeLiveTestCase, self).publish(*args, **kw)
      finally:
        restoreInteraction()

from Products.ERP5Type.dynamic.component_package import ComponentDynamicPackage, ComponentImportError
from Products.ERP5Type.tests.runUnitTest import ERP5TypeTestLoader

class ERP5TypeTestReLoader(ERP5TypeTestLoader):
    """ERP5Type test re-loader supports reloading test modules before
    running them.
    """

    def __init__(self, filter_test_list=()):
        super(ERP5TypeTestReLoader, self).__init__()
        if len(filter_test_list):
            # do not filter if no filter, otherwise no tests run
            self.filter_test_list = filter_test_list

    def loadTestsFromNames(self, test_list):
        # ERP5TypeTestLoader is monkey-patched into unittest
        # so we have to monkeypatch it in turn
        if self.filter_test_list is not None:
            old_filter_test_list = ERP5TypeTestLoader.filter_test_list
            ERP5TypeTestLoader.filter_test_list = self.filter_test_list
        try:
            return super(ERP5TypeTestReLoader,
                         self).loadTestsFromNames(test_list)
        finally:
            # and undo the monkeypatch afterwards
            if self.filter_test_list:
                ERP5TypeTestLoader.filter_test_list = old_filter_test_list

    def loadTestsFromName(self, name, module=None):
        """
        Load the test from the given name from ZODB if it can be imported,
        otherwise fallback on filesystem
        """
        if module is None:
            try:
                self._importZodbTestComponent(name.split('.')[0])
            except ComponentImportError:
                raise
            except ImportError:
                pass
            else:
                import erp5.component.test
                module = erp5.component.test

        return super(ERP5TypeTestReLoader, self).loadTestsFromName(name,
                                                                   module)

    def loadTestsFromModule(self, module):
        """
        If the module is not a ZODB Component, then reload it to consider
        modifications on the filesystem
        """
        if not isinstance(getattr(module, '__loader__', None),
                          ComponentDynamicPackage):
            reload(module)
        return super(ERP5TypeTestReLoader, self).loadTestsFromModule(module)

    def loadTestsFromTestCase(self, testCaseClass):
        testModule = sys.modules[testCaseClass.__module__]
        # Do not reload ERP5TypeTestCase, SecurityTestCase or ERP5ReportTestCase because we patch
        # it nor ZODB Test Component as it is reset upon modification anyway
        if (testCaseClass not in (ERP5TypeTestCase, SecurityTestCase, ERP5ReportTestCase) and
            not isinstance(getattr(testModule, '__loader__', None),
                           ComponentDynamicPackage)):
          testModule = reload(testModule)
        testCaseClass = getattr(testModule, testCaseClass.__name__)
        return ERP5TypeTestLoader.loadTestsFromTestCase(self, testCaseClass)

def runLiveTest(test_list, verbosity=1, stream=None, request_server_url=None, **kw):
  from Products.ERP5Type.tests.runUnitTest import DebugTestResult
  from six.moves import StringIO
  # Add path of the TestTemplateItem folder of the instance
  path = kw.get('path', None)
  if path is not None and path not in sys.path:
    sys.path.append(path)
  product_test_list = []
  import Products
  for product_path in Products.__path__:
    product_test_list.extend(glob(os.path.join(product_path, '*', 'tests')))
  current_syspath = set(sys.path)

  global _request_server_url
  _request_server_url = request_server_url

  sys.path.extend(path for path in product_test_list
                  if path not in current_syspath)

  TestRunner = unittest.TextTestRunner
  if ERP5TypeLiveTestCase not in ERP5TypeTestCase.__bases__:
    ERP5TypeTestCase.__bases__ = ERP5TypeLiveTestCase,
  if kw.get('debug', False):
    class DebugTextTestRunner(TestRunner):
      def _makeResult(self):
        result = super(DebugTextTestRunner, self)._makeResult()
        return DebugTestResult(result)
    TestRunner = DebugTextTestRunner
  run_only = kw.get('run_only', ())
  filter_test_list = [re.compile(x).search
                      for x in run_only]
  loader = ERP5TypeTestReLoader(filter_test_list)
  suite = loader.loadTestsFromNames(test_list)
  output = stream
  if stream is None:
    output = StringIO()
  def print_and_write(data):
    sys.stderr.write(data)
    sys.stderr.flush()
    return output.write(data)
  print_and_write("**Running Live Test:\n")
  ZopeTestCase._print = print_and_write

  with warnings.catch_warnings():
    warnings.simplefilter(kw['warnings'])

    # Test may login/logout with different users, so ensure that at the end the
    # original SecurityManager is restored
    from AccessControl.SecurityManagement import getSecurityManager, setSecurityManager
    sm = getSecurityManager()
    try:
      result = TestRunner(stream=output, verbosity=verbosity).run(suite)
    finally:
      setSecurityManager(sm)
