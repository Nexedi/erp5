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

class ERP5TypeLiveTestCase(ProcessingNodeTestCase, PortalTestCase):
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

    def shortDescription(self):
      description = str(self)
      doc = self._testMethodDoc
      if doc and doc.split("\n")[0].strip():
        description += ', ' + doc.split("\n")[0].strip()
      return description

    def getTitle(self):
      """Returns the title of the test, for test reports.
      """
      return str(self.__class__)

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

    def login(self, user_name='ERP5TypeTestCase', quiet=0):
      """
      Most of the time, we need to login before doing anything
      """
      PortalTestCase.login(self, user_name)

    def logout(self):
      PortalTestCase.logout(self)
      # clean up certain cache related REQUEST keys that might be associated
      # with the logged in user
      for key in ('_ec_cache', '_oai_cache'):
        pass
        #self.REQUEST.other.pop(key, None) # XXX

    def _close(self):
      '''Closes the ZODB connection.'''
      transaction.abort()

    # class-defined decorators for profiling.
    # Depending on the environment variable, they return
    # the same method, or a profiling wrapped call
    _decorate_setUp = profile_if_environ('PROFILE_SETUP')
    _decorate_testRun = profile_if_environ('PROFILE_TESTS')
    _decorate_tearDown = profile_if_environ('PROFILE_TEARDOWN')

    def __call__(self, *args, **kw):
      # Pulling down the profiling from ZopeTestCase.profiler to allow
      # overriding run()
      # This cannot be done at instanciation because we need to
      # wrap the bottom-most methods, e.g.
      # SecurityTestCase.tearDown instead of ERP5TestCase.tearDown

      self.setUp = self._decorate_setUp(self.setUp)
      self.tearDown = self._decorate_tearDown(self.tearDown)

      test_name = self._testMethodName
      test_method = getattr(self, test_name)
      setattr(self, test_name, self._decorate_testRun(test_method))

      self.run(*args, **kw)

    def _setup(self):
        '''Configures the portal. Framework authors may
           override.
        '''
        pass # Do nothing in a live test

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
      '''Called after setUp() has completed. This is
         far and away the most useful hook.
      '''
      pass

    def beforeClear(self):
      '''Called before _clear(). Subclasses should
      use it to garbage collect objects which must not remain
      in the system
      '''
      pass

    def logMessage(self, message):
      """
        Shortcut function to log a message
      """
      ZopeTestCase._print('\n%s ' % message)
      LOG('Testing ... ', DEBUG, message)

    # Utility methods specific to ERP5Type
    def getTemplateTool(self):
      return getToolByName(self.getPortal(), 'portal_templates', None)

    def getPreferenceTool(self) :
      return getToolByName(self.getPortal(), 'portal_preferences', None)

    def getTrashTool(self):
      return getToolByName(self.getPortal(), 'portal_trash', None)

    def getPasswordTool(self):
      return getToolByName(self.getPortal(), 'portal_password', None)

    def getSkinsTool(self):
      return getToolByName(self.getPortal(), 'portal_skins', None)

    def getCategoryTool(self):
      return getToolByName(self.getPortal(), 'portal_categories', None)

    def getWorkflowTool(self):
      return getToolByName(self.getPortal(), 'portal_workflow', None)

    def getCatalogTool(self):
      return getToolByName(self.getPortal(), 'portal_catalog', None)

    def getTypesTool(self):
      return getToolByName(self.getPortal(), 'portal_types', None)
    getTypeTool = getTypesTool

    def getRuleTool(self):
      return getattr(self.getPortal(), 'portal_rules', None)

    def getClassTool(self):
      return getattr(self.getPortal(), 'portal_classes', None)

    def getSimulationTool(self):
      return getToolByName(self.getPortal(), 'portal_simulation', None)

    def getSQLConnection(self):
      return getToolByName(self.getPortal(), 'erp5_sql_connection', None)

    def getPortalId(self):
      return self.getPortal().getId()

    def getDomainTool(self):
      return getToolByName(self.getPortal(), 'portal_domains', None)

    def getAlarmTool(self):
      return getattr(self.getPortal(), 'portal_alarms', None)

    def getActivityTool(self):
      return getattr(self.getPortal(), 'portal_activities', None)

    def getArchiveTool(self):
      return getattr(self.getPortal(), 'portal_archives', None)

    def getCacheTool(self):
      return getattr(self.getPortal(), 'portal_caches', None)

    def getOrganisationModule(self):
      return getattr(self.getPortal(), 'organisation_module',
          getattr(self.getPortal(), 'organisation', None))

    def getPersonModule(self):
      return getattr(self.getPortal(), 'person_module',
          getattr(self.getPortal(), 'person', None))

    def getCurrencyModule(self):
      return getattr(self.getPortal(), 'currency_module',
          getattr(self.getPortal(), 'currency', None))

    def validateRules(self):
      """
      try to validate all rules in rule_tool.
      """
      rule_tool = self.getRuleTool()
      for rule in rule_tool.contentValues(
          portal_type=rule_tool.getPortalRuleTypeList()):
        if rule.getValidationState() != 'validated':
          rule.validate()

    def createSimpleUser(self, title, reference, function):
      """
        Helper function to create a Simple ERP5 User.
        User password is the reference.
        
        XXX-JPS do wa have a "delete" method etc.
      """
      user = self.createUser(reference, person_kw=dict(title=title))
      assignment = self.createUserAssignement(user, assignment_kw=dict(function=function))
      return user

    def createUser(self, reference, password=None, person_kw=None):
      """
        Create an ERP5 User.
        Default password is the reference.
        person_kw is passed as additional arguments when creating the person
      """
      if password is None:
        password = reference
      if person_kw is None:
        person_kw = dict()

      person = self.portal.person_module.newContent(portal_type='Person',
                                                    reference=reference,
                                                    password=password,
                                                    **person_kw)
      return person

    def createUserAssignment(self, user, assignment_kw):
      """
        Create an assignment to user.
      """
      assignment = user.newContent(portal_type='Assignment', **assignment_kw)
      assignment.open()
      return assignment

    def createUserAssignement(self, user, assignment_kw):
      # BBB
      warn('createUserAssignement is deprecated;'
           'Use createUserAssignment instead',
           DeprecationWarning)
      return self.createUserAssignment(user, assignment_kw)

    def failIfDifferentSet(self, a, b, msg=""):
      if not msg:
        msg='%r != %r' % (a, b)
      for i in a:
        self.failUnless(i in b, msg)
      for i in b:
        self.failUnless(i in a, msg)
      self.assertEquals(len(a), len(b), msg)
    assertSameSet = failIfDifferentSet

    def assertWorkflowTransitionFails(self, object, workflow_id, transition_id,
        error_message=None, state_variable='simulation_state'):
      """
        Check that passing given transition from given workflow on given object
        raises ValidationFailed.
        Do sanity checks (workflow history length increased by one, simulation
        state unchanged).
        If error_message is provided, it is asserted to be equal to the last
        workflow history error message.
      """
      workflow_tool = self.getWorkflowTool()
      reference_history_length = len(workflow_tool.getInfoFor(ob=object, name='history', wf_id=workflow_id))
      state_method = 'get' + convertToUpperCase(state_variable)
      method = getattr(object, state_method, None)
      reference_workflow_state = method()
      self.assertRaises(ValidationFailed, workflow_tool.doActionFor, object, transition_id, wf_id=workflow_id)
      workflow_history = workflow_tool.getInfoFor(ob=object, name='history', wf_id=workflow_id)
      self.assertEqual(len(workflow_history), reference_history_length + 1)
      workflow_error_message = str(workflow_history[-1]['error_message'])
      if error_message is not None:
        self.assertEqual(workflow_error_message, error_message)
      self.assertEqual(method(), reference_workflow_state)
      return workflow_error_message

    def tearDown(self):
      '''Tears down the fixture. Do not override,
         use the hooks instead.
      '''
      PortalTestCase.tearDown(self)

    def beforeClose(self):
      """
      Clear "my activities"... how to do this ?
      """
      PortalTestCase.beforeClose(self)

    def stepPdb(self, sequence=None, sequence_list=None):
      """Invoke debugger"""
      try: # try ipython if available
        import IPython
        IPython.Shell.IPShell(argv=[])
        tracer = IPython.Debugger.Tracer()
      except ImportError:
        from pdb import set_trace as tracer
      tracer()

    def stepTic(self, **kw):
      """
      The is used to simulate the zope_tic_loop script
      Each time this method is called, it simulates a call to tic
      which invoke activities in the Activity Tool
      """
      if kw.get('sequence', None) is None:
        # in case of using not in sequence commit transaction
        transaction.commit()
      self.tic()

    def publish(self, path, basic=None, env=None, extra=None,
                request_method='GET', stdin=None, handle_errors=True):
        '''Publishes the object at 'path' returning a response object.'''

        from ZPublisher.Response import Response
        from ZPublisher.Test import publish_module

        from AccessControl.SecurityManagement import getSecurityManager
        from AccessControl.SecurityManagement import setSecurityManager
        
        # Save current security manager
        sm = getSecurityManager()

        # Commit the sandbox for good measure
        transaction.commit()

        if env is None:
            env = {}
        if extra is None:
            extra = {}

        request = self.app.REQUEST

        env['SERVER_NAME'] = request['SERVER_NAME']
        env['SERVER_PORT'] = request['SERVER_PORT']
        env['HTTP_ACCEPT_CHARSET'] = request['HTTP_ACCEPT_CHARSET']
        env['REQUEST_METHOD'] = request_method

        p = path.split('?')
        if len(p) == 1:
            env['PATH_INFO'] = p[0]
        elif len(p) == 2:
            [env['PATH_INFO'], env['QUERY_STRING']] = p
        else:
            raise TypeError, ''

        if basic:
            env['HTTP_AUTHORIZATION'] = "Basic %s" % base64.encodestring(basic).replace('\012', '')

        if stdin is None:
            stdin = StringIO()

        outstream = StringIO()
        response = Response(stdout=outstream, stderr=sys.stderr)

        publish_module('Zope2',
                       response=response,
                       stdin=stdin,
                       environ=env,
                       extra=extra,
                       debug=not handle_errors,
                      )

        # Restore security manager
        setSecurityManager(sm)

        return ResponseWrapper(response, outstream, path)

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
  # Reload the test class before runing tests
  for test_name in test_list:
    (test_file, test_path_name, test_description) = imp.find_module(test_name)
    imp.load_module(test_name, test_file, test_path_name, test_description)

  TestRunner = backportUnittest.TextTestRunner
  if kw.get('debug', False):
    class DebugTextTestRunner(TestRunner):
      def _makeResult(self):
        result = super(DebugTextTestRunner, self)._makeResult()
        return DebugTestResult(result)
    TestRunner = DebugTextTestRunner
  loader = ERP5TypeTestLoader()
  run_only = kw.get('run_only', None)
  if run_only is not None:
    loader.filter_test_list = [re.compile(x).search for x in run_only.split(',')]
  suite = loader.loadTestsFromNames(test_list)
  output = stream
  if stream is None:
    output = StringIO()
  output.write("**Running Live Test:\n")
  result = TestRunner(stream=output, verbosity=verbosity).run(suite)
