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
      return self.getPortalObject().getId()

    def getPortal(self):
      """Returns the portal object, i.e. the "fixture root".
      """
      # Assumes that portal exists (which has sense) and that there is only one
      # ERP5 site in Zope (which is always the case)
      if self.app.meta_type == 'ERP5 Site':
        return self.app
      return [q for q in self.app.objectValues() if q.meta_type == 'ERP5 Site'
          ][0]

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
      transaction.abort()

    def _setup(self):
        '''Change some site properties in order to be ready for live test
        '''
        # Disabling portal_activities is required in order to avoid
        # conflict with other threads doing tic in the same time
        self.initial_transaction_hash = transaction.get().__hash__()
        self.activity_tool_subscribed = self.getPortalObject()\
                .portal_activities.isSubscribed()
        self.portal.portal_activities.unsubscribe()

    def setUp(self):
        '''Sets up the fixture. Do not override,
           use the hooks instead.
        '''
        try:
            self.beforeSetUp()
            self.app = self._app()
            self.portal = self._portal()
            self._setup()
            self.afterSetUp()
        except:
            self.beforeClear()
            self._clear()
            raise

    def _app(self):
        '''Returns the app object for a test.'''
        request = get_request()
        return request.PARENTS[-1]

    def afterSetUp(self):
      '''Called after setUp() has completed. This is
         far and away the most useful hook.
      '''
      pass

    def beforeSetUp(self):
      '''Called before the ZODB connection is opened,
           at the start of setUp(). By default begins
           a new transaction.
      '''
      pass

    def beforeClear(self):
      '''Called before _clear(). Subclasses should
      use it to garbage collect objects which must not remain
      in the system
      '''
      pass

    def tearDown(self):
      '''Tears down the fixture. Do not override,
         use the hooks instead.
      '''
      PortalTestCase.tearDown(self)

    def beforeClose(self):
      """
      put back site properties that were disabled for unit test
      """
      if transaction.get().__hash__() != self.initial_transaction_hash:
        if self.activity_tool_subscribed:
          self.portal.portal_activities.subscribe()
          transaction.commit()
      PortalTestCase.beforeClose(self)

def runLiveTest(test_list, verbosity=1, stream=None, **kw):
  from Products.ERP5Type.tests.runUnitTest import DebugTestResult
  from Products.ERP5Type.tests.runUnitTest import ERP5TypeTestLoader
  from Products.ERP5Type.tests import backportUnittest
  from StringIO import StringIO
  import imp
  import re
  # Add path of the TestTemplateItem folder of the instance
  path = kw.get('path', None)
  if path is not None and path not in sys.path:
    sys.path.append(path)
  product_test_list = []
  import Products
  for product_path in Products.__path__:
    product_test_list.extend(glob(os.path.join(product_path, '*', 'tests')))

  sys.path.extend(product_test_list)
  # Reload the test class before runing tests
  for test_name in test_list:
    (test_file, test_path_name, test_description) = imp.find_module(test_name)
    imp.load_module(test_name, test_file, test_path_name, test_description)

  TestRunner = backportUnittest.TextTestRunner
  if ERP5TypeLiveTestCase not in ERP5TypeTestCase.__bases__:
    ERP5TypeTestCase.__bases__ = ERP5TypeLiveTestCase,
  if kw.get('debug', False):
    class DebugTextTestRunner(TestRunner):
      def _makeResult(self):
        result = super(DebugTextTestRunner, self)._makeResult()
        return DebugTestResult(result)
    TestRunner = DebugTextTestRunner
  loader = ERP5TypeTestLoader()
  run_only = kw.get('run_only', None)
  if run_only is not None:
    ERP5TypeTestLoader.filter_test_list = \
        [re.compile(x).search for x in run_only.split(',')]
  suite = loader.loadTestsFromNames(test_list)
  if run_only is not None:
    ERP5TypeTestLoader.filter_test_list = None
  output = stream
  if stream is None:
    output = StringIO()
  output.write("**Running Live Test:\n")
  result = TestRunner(stream=output, verbosity=verbosity).run(suite)
