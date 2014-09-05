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
import thread

from Testing import ZopeTestCase
from Testing.ZopeTestCase import PortalTestCase, user_name
from Products.CMFCore.utils import getToolByName
from Products.ERP5Type.tests.ProcessingNodeTestCase import ProcessingNodeTestCase
from Products.ERP5Type.Globals import get_request
from Products.ERP5Type.tests.ERP5TypeTestCase import \
  ERP5TypeTestCaseMixin, ERP5TypeTestCase
from glob import glob
import transaction

from zLOG import LOG, DEBUG, INFO

# Disable patching of activity tool,
# Tic doesn't need help as TimerService is running
from Products.ERP5Type.tests import ProcessingNodeTestCase as\
                                    ProcessingNodeTestCaseModule
ProcessingNodeTestCaseModule.patchActivityTool = lambda: None


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

    def getPortalName(self):
      """ Return the default ERP5 site id.
      """
      return self.portal.getId()

    def getPortal(self):
      """Returns the portal object, i.e. the "fixture root".

      Rewrap the portal in an independant request for this test.
      """
      if self.portal is not None:
        return self.portal

      # _module_cache_set is used to keep a reference to the code of modules
      # before they get reloaded. As we will use another request we need to
      # make sure that we still have a reference to _module_cache_set so that
      # it does not get garbage collected.
      module_cache_set = getattr(get_request(), '_module_cache_set', None)

      from Products.ERP5.ERP5Site import getSite
      site = getSite()
      # reconstruct the acquistion chain with an independant request.
      #   RequestContainer -> Application -> Site
      from Testing.ZopeTestCase.utils import makerequest
      portal = getattr(makerequest(site.aq_parent), site.getId())

      if module_cache_set:
        portal.REQUEST._module_cache_set = module_cache_set

      # Make the various get_request patches return this request.
      # This is for ERP5TypeTestCase patch
      from Testing.ZopeTestCase.connections import registry
      if registry:
        registry._conns[-1] = portal

      # This is for Localizer patch
      from Products.Localizer import patches
      request = portal.REQUEST
      with patches._requests_lock:
        patches._requests[thread.get_ident()] = request

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
      revert = transaction.get().__hash__() != self.initial_transaction_hash
      self.abort()
      self._restoreMailHost()
      if revert:
        if self.activity_tool_subscribed:
          self.portal.portal_activities.subscribe()
          self.commit()

    def _setup(self):
        '''Change some site properties in order to be ready for live test
        '''
        # Disabling portal_activities is required in order to avoid
        # conflict with other threads doing tic in the same time
        self.login()
        self.initial_transaction_hash = transaction.get().__hash__()
        self.activity_tool_subscribed = self.getPortalObject()\
                .portal_activities.isSubscribed()
        self.portal.portal_activities.unsubscribe()
        self._setUpDummyMailHost()

    setUp = PortalTestCase.setUp
    tearDown = PortalTestCase.tearDown

    def _app(self):
        '''Returns the app object for a test.'''
        return self.getPortal().aq_parent

    def afterSetUp(self):
      '''Called after setUp() has completed. This is
         far and away the most useful hook.
      '''
      pass

from Products.ERP5Type.dynamic.component_package import ComponentDynamicPackage
from Products.ERP5Type.tests.runUnitTest import ERP5TypeTestLoader

class ERP5TypeLiveTestLoader(ERP5TypeTestLoader):
    """
    ERP5Type Live Test loader which allows to load ZODB Components if any
    """
    def loadTestsFromName(self, name, module=None):
        """
        Load the test from the given name from ZODB if it can be imported,
        otherwise fallback on filesystem
        """
        if module is None:
            import erp5.component.test

            try:
                __import__('erp5.component.test.' + name,
                           fromlist=['erp5.component.test'],
                           level=0)
            except ImportError:
                raise
            else:
                module = erp5.component.test

        return super(ERP5TypeLiveTestLoader, self).loadTestsFromName(name,
                                                                     module)

def runLiveTest(test_list, verbosity=1, stream=None, **kw):
  from Products.ERP5Type.tests.runUnitTest import DebugTestResult
  from Products.ERP5Type.tests import backportUnittest
  from StringIO import StringIO
  # Add path of the TestTemplateItem folder of the instance
  path = kw.get('path', None)
  if path is not None and path not in sys.path:
    sys.path.append(path)
  product_test_list = []
  import Products
  for product_path in Products.__path__:
    product_test_list.extend(glob(os.path.join(product_path, '*', 'tests')))
  current_syspath = set(sys.path)

  sys.path.extend(path for path in product_test_list
                  if path not in current_syspath)

  TestRunner = backportUnittest.TextTestRunner
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
  loader = ERP5TypeLiveTestLoader(filter_test_list)
  suite = loader.loadTestsFromNames(test_list)
  output = stream
  if stream is None:
    output = StringIO()
  output.write("**Running Live Test:\n")
  ZopeTestCase._print = output.write

  # Test may login/logout with different users, so ensure that at the end the
  # original SecurityManager is restored
  from AccessControl.SecurityManagement import getSecurityManager, setSecurityManager
  sm = getSecurityManager()
  try:
    result = TestRunner(stream=output, verbosity=verbosity).run(suite)
  finally:
    setSecurityManager(sm)
