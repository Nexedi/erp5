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

def profile_if_environ(environment_var_name):
    if int(os.environ.get(environment_var_name, 0)):
      def decorator(self, method):
        def decorated():
          self.runcall(method)
        decorated.__name__ = method.__name__
        decorated.__doc__ = method.__doc__
        return decorated
      return decorator
    else:
      # No profiling, return identity decorator
      return lambda self, method: method

# Disable patching of activity tool, 
# Tic doesn't need help as TimserService is running
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

    def getPortalName(self):
      """ Return the default ERP5 site id.
      """
      return self.portal.getId()

    def getPortal(self):
      """Returns the portal object, i.e. the "fixture root".
      """
      from Products.ERP5.ERP5Site import getSite
      return getSite(get_request())

    getPortalObject = getPortal

    #def logout(self):
    #  PortalTestCase.logout(self)
    #  # clean up certain cache related REQUEST keys that might be associated
    #  # with the logged in user
    #  for key in ('_ec_cache', '_oai_cache'):
    #    pass
    #    #self.REQUEST.other.pop(key, None) # XXX

    def _close(self):
      '''Closes the ZODB connection.'''
      revert = transaction.get().__hash__() != self.initial_transaction_hash
      transaction.abort()
      self._restoreMailHost()
      if revert:
        if self.activity_tool_subscribed:
          self.portal.portal_activities.subscribe()
          transaction.commit()

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

    def loadTestsFromModule(self, module):
        reload(module)
        return super(ERP5TypeTestReLoader, self).loadTestsFromModule(module)

    def loadTestsFromTestCase(self, testCaseClass):
        testModule = sys.modules[testCaseClass.__module__]
        if not(testCaseClass is ERP5TypeTestCase):
          # do not reload ERP5TypeTestCase because we patch it
          testModule = reload(testModule)
        testCaseClass = getattr(testModule, testCaseClass.__name__)
        return super(ERP5TypeTestReLoader,
                     self).loadTestsFromTestCase(testCaseClass)

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
  loader = ERP5TypeTestReLoader(filter_test_list)
  suite = loader.loadTestsFromNames(test_list)
  output = stream
  if stream is None:
    output = StringIO()
  output.write("**Running Live Test:\n")
  ZopeTestCase._print = output.write
  result = TestRunner(stream=output, verbosity=verbosity).run(suite)
