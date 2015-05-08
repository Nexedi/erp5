# -*- coding: utf-8 -*-
# Derived from PloneTestCase in Plone.

#
# ERP5TypeTestCase
#

__version__ = '0.3.0'

import base64
import errno
import httplib
import os
import random
import re
import socket
import sys
import time
import traceback
import urllib
import ConfigParser
from cStringIO import StringIO
from cPickle import dumps
from glob import glob
from hashlib import md5
from warnings import warn
from ExtensionClass import pmc_init_of
from DateTime import DateTime

# XXX make sure that get_request works.
import Products.ERP5Type.Utils
from Products.ERP5Type import Globals

# store a copy of the original method
original_get_request = Globals.get_request
convertToUpperCase = Products.ERP5Type.Utils.convertToUpperCase

from Testing.ZopeTestCase.connections import registry
def get_context():
  if registry:
    return registry._conns[-1]

def get_request():
  request = original_get_request()
  if request is not None:
    return request
  current_app = get_context()
  if current_app is not None:
    return current_app.REQUEST

Products.ERP5Type.Utils.get_request = get_request
Globals.get_request = get_request

from zope.site.hooks import setSite

from Testing import ZopeTestCase
from Testing.ZopeTestCase import PortalTestCase, user_name
from Products.CMFCore.utils import getToolByName
from Products.DCWorkflow.DCWorkflow import ValidationFailed
from Products.ERP5Type.Accessor.Constant import PropertyGetter as ConstantGetter
from zLOG import LOG, DEBUG

from Products.ERP5Type.tests.backportUnittest import SetupSiteError
from Products.ERP5Type.tests.utils import addUserToDeveloperRole
from Products.ERP5Type.tests.utils import DummyMailHostMixin, parseListeningAddress

# Quiet messages when installing business templates
install_bt5_quiet = 0

from App.config import getConfiguration

config = getConfiguration()
instancehome = config.instancehome
# Make sure we can call manage_debug_threads on a test instance
if getattr(config, 'product_config', None) is None:
  config.product_config = {}
config.product_config['deadlockdebugger'] = {'dump_url':'/manage_debug_threads'}

from Testing.ZopeTestCase.layer import onsetup

try:
  # Workaround Localizer >= 1.2 patch that doesn't work with
  # ZopeTestCase REQUESTs
  from Products.Localizer import patches, utils
  # revert monkey patches from Localizer
  patches.get_request = get_request
  utils.get_request = get_request
except ImportError:
  pass

from Products.ERP5Type.tests.ProcessingNodeTestCase import \
  ProcessingNodeTestCase, patchActivityTool
onsetup(patchActivityTool)()

from AccessControl.SecurityManagement import newSecurityManager, noSecurityManager

from Acquisition import aq_base

portal_name = 'erp5_portal'

# we keep a reference to all sites for which setup failed the first time, to
# prevent replaying the same failing setup step for each test.
failed_portal_installation = {}

# have we installed business templates ?
# this is a mapping 'list of business template -> boolean
setup_done = set()

def _getConnectionStringDict():
  """Returns the connection strings used for this test.
  """
  connection_string_dict = {}
  default = os.environ.get('erp5_sql_connection_string')
  for connection in ('erp5_sql_connection_string',
                     'erp5_sql_deferred_connection_string',
                     # default value for transactionless is derived from value
                     # for cmf_activity, so process it last
                     'cmf_activity_sql_connection_string'):
    connection_string = os.environ.get(connection, default)
    if connection_string:
      connection_string_dict[connection] = connection_string
  connection = 'erp5_sql_transactionless_connection_string'
  if os.environ.get(connection, connection_string):
    connection_string_dict[connection] = \
      os.environ.get(connection, '-' + connection_string)
  return connection_string_dict

def _getConversionServerDict():
  """ Returns a dict with hostname and port for Conversion Server (Oood)
  """
  conversion_server_hostname = os.environ.get('conversion_server_hostname',
                                              'localhost')
  conversion_server_port = os.environ.get('conversion_server_port',
                                          '8008')
  return dict(hostname=conversion_server_hostname,
              port=int(conversion_server_port))

def _getVolatileMemcachedServerDict():
  """Returns a dict with hostname and port for volatile memcached Server
  """
  hostname = os.environ.get('volatile_memcached_server_hostname',
                            'localhost')
  port = os.environ.get('volatile_memcached_server_port', '11211')
  return dict(hostname=hostname, port=port)

def _getPersistentMemcachedServerDict():
  """Returns a dict with hostname and port for persistent memcached Server
  """
  hostname = os.environ.get('persistent_memcached_server_hostname',
                            'localhost')
  port = os.environ.get('persistent_memcached_server_port', '12121')
  return dict(hostname=hostname, port=port)

def _createTestPromiseConfigurationFile(promise_path):
  kumofs_url = "memcached://%(hostname)s:%(port)s/" % \
                             _getVolatileMemcachedServerDict()
  memcached_url = "memcached://%(hostname)s:%(port)s/" % \
                             _getPersistentMemcachedServerDict()
  cloudooo_url = "cloudooo://%(hostname)s:%(port)s/" % \
                             _getConversionServerDict()

  promise_config = ConfigParser.RawConfigParser()
  promise_config.add_section('external_service')
  promise_config.set('external_service', 'cloudooo_url', cloudooo_url)
  promise_config.set('external_service', 'memcached_url',memcached_url)
  promise_config.set('external_service', 'kumofs_url', kumofs_url)

  if os.environ.get('TEST_CA_PATH') is not None:
    promise_config.add_section('portal_certificate_authority')
    promise_config.set('portal_certificate_authority', 'certificate_authority_path',
                                           os.environ['TEST_CA_PATH'])

  promise_config.write(open(promise_path, 'w'))

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

# Patch DateTime to allow pinning the notion of "now".
assert getattr(DateTime, '_original_parse_args', None) is None
DateTime._original_parse_args = DateTime._parse_args

_pinned_date_time = None

def _parse_args(self, *args, **kw):
  if _pinned_date_time is not None and (not args or args[0] == None):
    # simulate fixed "Now"
    args = (_pinned_date_time,) + args[1:]
  return self._original_parse_args(*args, **kw)

_parse_args._original = DateTime._original_parse_args
DateTime._parse_args = _parse_args

class ERP5TypeTestCaseMixin(ProcessingNodeTestCase, PortalTestCase):
    """Mixin class for ERP5 based tests.
    """

    def dummy_test(self):
      ZopeTestCase._print('All tests are skipped when --save option is passed '
                          'with --update_business_templates or without --load')

    def getRevision(self):
      erp5_path = os.path.join(instancehome, 'Products', 'ERP5')
      try:
        import pysvn
        return pysvn.Client().info(erp5_path).revision.number
      except Exception:
        return None

    def getTitle(self):
      """Returns the title of the test, for test reports.
      """
      return str(self.__class__)

    def login(self, user_name='ERP5TypeTestCase', quiet=0):
      """
      Most of the time, we need to login before doing anything
      """
      try:
        PortalTestCase.login(self, user_name)
      except AttributeError:
        uf = self.getPortal().acl_users
        uf._doAddUser('ERP5TypeTestCase', '', ['Manager', 'Member', 'Assignee',
                      'Assignor', 'Author', 'Auditor', 'Associate'], [])
        return PortalTestCase.login(self, user_name)

    def changeSkin(self, skin_name):
      """
        Change current Skin
      """
      request = self.app.REQUEST
      self.getPortal().portal_skins.changeSkin(skin_name)
      request.set('portal_skin', skin_name)

    def logout(self):
      PortalTestCase.logout(self)
      # clean up certain cache related REQUEST keys that might be associated
      # with the logged in user
      if getattr(self, 'REQUEST', None) is not None:
        for key in ('_ec_cache', '_oai_cache'):
          self.REQUEST.other.pop(key, None)

    def _setupUser(self):
      '''Creates the default user.'''
      uf = self.portal.acl_users
      # do nothing if the user already exists
      if not uf.getUser(user_name):
        uf._doAddUser(user_name, 'secret', ['Member'], [])

    def _setUpDummyMailHost(self):
      """Replace Original Mail Host by Dummy Mail Host in a non-persistent way
      """
      cls = self.portal.MailHost.__class__
      if not issubclass(cls, DummyMailHostMixin):
        cls.__bases__ = (DummyMailHostMixin,) + cls.__bases__
        pmc_init_of(cls)

    def _restoreMailHost(self):
      """Restore original Mail Host
      """
      cls = self.portal.MailHost.__class__
      if cls.__bases__[0] is DummyMailHostMixin:
        cls.__bases__ = cls.__bases__[1:]
        pmc_init_of(cls)

    def pinDateTime(self, date_time):
      # pretend time has stopped at a certain date (i.e. the test runs
      # infinitely fast), to avoid errors on tests that are started
      # just before midnight.
      global _pinned_date_time
      assert date_time is None or isinstance(date_time, DateTime)
      _pinned_date_time = date_time

    def unpinDateTime(self):
      self.pinDateTime(None)

    def getDefaultSitePreferenceId(self):
      """Default id, usefull method to override
      """
      return "default_site_preference"

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

    def _addPropertySheet(self, portal_type_name,
                          property_sheet_name='TestPropertySheet',
                          deprecated=None):
      """Utility method to add a property sheet to a type information.
      You might be interested in the higer level method _addProperty
      This method registers all added property sheets, to be able to remove
      them in tearDown.
      """
      if deprecated is not None:
        raise ValueError("Please update this test to use ZODB property sheets")

      portal_property_sheets = self.portal.portal_property_sheets
      property_sheet = getattr(portal_property_sheets, property_sheet_name, None)
      if property_sheet is None:
        property_sheet = portal_property_sheets.newContent(id=property_sheet_name)

      # We set the property sheet on the portal type
      types_tool = self.getTypesTool()
      ti = types_tool.getTypeInfo(portal_type_name)
      property_sheet_set = set(ti.getTypePropertySheetList())
      property_sheet_set.add(property_sheet_name)
      ti.setTypePropertySheetList(list(property_sheet_set))

      # remember that we added a property sheet for tear down
      self._added_property_sheets.setdefault(
                    portal_type_name, []).append(property_sheet_name)

      return property_sheet

    def getRule(self, **kw):
      return self.portal.portal_rules.searchFolder(
          sort_on='version', sort_order='descending', **kw)[0].getObject()

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
        person_kw = {}

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

    @staticmethod
    def _getBTPathAndIdList(template_list):
      bootstrap_path = os.environ.get('erp5_tests_bootstrap_path') or \
        ERP5Site.getBootstrapDirectory()
      bt5_path = os.environ.get('erp5_tests_bt5_path')
      if bt5_path:
        bt5_path_list = bt5_path.split(',')
        bt5_path_list += [os.path.join(path, "*") for path in bt5_path_list]
      else:
        bt5_path = os.path.join(instancehome, 'bt5')
        bt5_path_list = bt5_path, os.path.join(bt5_path, '*')

      def search(path, template):
        urltype, url = urllib.splittype(path + '/' + template)
        if urltype == 'http':
          host, selector = urllib.splithost(url)
          user_passwd, host = urllib.splituser(host)
          host = urllib.unquote(host)
          h = httplib.HTTP(host)
          h.putrequest('HEAD', selector)
          h.putheader('Host', host)
          if user_passwd:
            h.putheader('Authorization',
                        'Basic %s' % base64.b64encode(user_passwd).strip())
          h.endheaders()
          errcode, errmsg, headers = h.getreply()
          if errcode == 200:
            return urltype + ':' + url
        else:
          path_list = glob(os.path.join(os.path.expanduser(path), template))
          if path_list:
            return path_list[0]

      not_found_list = []
      new_template_list = []
      for template in template_list:
        id = template.split('/')[-1]
        for path in bt5_path_list:
          path = search(path, template) or search(path, template + '.bt5')
          if path:
            break
        else:
          path = os.path.join(bootstrap_path, template)
          if not os.path.exists(path):
            not_found_list.append(template)
            continue
        new_template_list.append((path, id))
      if not_found_list:
        raise RuntimeError("Following BT can't be found on your system : %s"
                           % ', '.join(not_found_list))
      return new_template_list

    def setupAutomaticBusinessTemplateRepository(self,
                              searchable_business_template_list=("erp5_base",)):
      template_tool = self.portal.portal_templates
      bt_set = set(searchable_business_template_list).difference(x['title']
        for x in template_tool.repository_dict.itervalues() for x in x)
      if bt_set:
        template_tool.updateRepositoryBusinessTemplateList(
          {os.path.dirname(x[0]) for x in self._getBTPathAndIdList(bt_set)},
          genbt5list=1)

    def assertSameSet(self, a, b, msg=None):
      self.assertSetEqual(set(a), set(b), msg)
    failIfDifferentSet = assertSameSet

    def assertHasAttribute(self, obj, attribute, msg=None):
      self.assertNotEqual(None, getattr(obj, attribute, None),
                       msg or "'%r': no attribute '%s'" % (obj,
                                                           attribute))

    def failIfHasAttribute(self, obj, attribute, msg=None):
      self.assertEqual(None, getattr(obj, attribute, None),
                        msg or "'%r': attribute '%s' present" % (obj,
                                                                 attribute))

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

    def stepPdb(self, sequence=None, sequence_list=None):
      """Invoke debugger"""
      try: # try ipython if available
        import IPython
        try:
          IPython.InteractiveShell()
          tracer = IPython.core.debugger.Tracer()
        except AttributeError: # for ipython-0.10 or before
          IPython.Shell.IPShell(argv=[])
          tracer = IPython.Debugger.Tracer()
      except ImportError:
        from pdb import set_trace as tracer
      tracer()

    def stepIPython(self, sequence=None, sequence_list=None):
      import IPython
      try:
        ipshell = IPython.frontend.terminal.embed.InteractiveShellEmbed()
      except AttributeError: # for ipython-0.10 or before
        ipshell = IPython.Shell.IPShellEmbed(())
      ipshell()

    def stepTic(self, sequence):
      """
      The is used to simulate the zope_tic_loop script
      Each time this method is called, it simulates a call to tic
      which invoke activities in the Activity Tool
      """
      self.tic()

    def getPortalObject(self):
      return self.getPortal()

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

    def logMessage(self, message):
      """
        Shortcut function to log a message
      """
      ZopeTestCase._print('\n%s ' % message)
      LOG('Testing ... ', DEBUG, message)

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
        self.commit()

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

    def getConsistencyMessageList(self, obj):
        return sorted([ str(message.getMessage())
                        for message in obj.checkConsistency() ])

    def _callSetUpOnce(self):
      setup_once = getattr(self, 'setUpOnce', None)
      if setup_once is not None and \
             not getattr(self.portal, 'set_up_once_called', 0):
        self.portal.set_up_once_called = 1
        ZopeTestCase._print('Executing setUpOnce ... ')
        start = time.time()
        setup_once()
        ZopeTestCase._print('done (%.3fs)\n' % (time.time() - start))

class ERP5TypeCommandLineTestCase(ERP5TypeTestCaseMixin):

    def getPortalName(self):
      """
        Return the name of a portal for this test case.
        This is necessary for each test case to use a different portal built by
        different business templates.
        The test runner can set `erp5_tests_portal_id` environment variable
        to force a portal id.
      """
      forced_portal_id = os.environ.get('erp5_tests_portal_id')
      if forced_portal_id:
        return str(forced_portal_id)
      m = md5(repr(self.getBusinessTemplateList()) + self.getTitle())
      return portal_name + '_' + m.hexdigest()

    def getPortal(self):
      """Returns the portal object, i.e. the "fixture root".

      It also does some initialization, as if the portal was accessed for the
      first time for the current request.
      For performance reason, this should be used in only 3 places:
      'setUpERP5Site', 'tic' and 'PortalTestCase._portal'
      """
      portal = self.app[self.getPortalName()]
      # Make sure skins are correctly set-up (it's not implicitly set up
      # by Acquisition on recent Zope)
      portal.setupCurrentSkin(portal.REQUEST)
      self.REQUEST = portal.REQUEST
      setSite(portal)
      return portal

    def _app(self):
      '''Opens a ZODB connection and returns the app object.

      We override it to patch HTTP_ACCEPT_CHARSET into REQUEST to get the zpt
      unicode conflict resolver to work properly'''
      app = PortalTestCase._app(self)
      app.REQUEST['HTTP_ACCEPT_CHARSET'] = 'utf-8'
      return app

    def enableLightInstall(self):
      """
      You can override this. Return if we should do a light install (1) or not (0)
      """
      return 1

    def enableActivityTool(self):
      """
      You can override this. Return if we should create (1) or not (0) an activity tool
      """
      return 1

    def enableHotReindexing(self):
      """
      You can override this. Return if we should create (1) or not (0) an activity tool
      """
      return 0

    def manuallyInstallBusinessTemplate(self, *template_list):
      new_template_list = self._getBTPathAndIdList(template_list)
      light_install = self.enableLightInstall()
      self._installBusinessTemplateList(new_template_list,
                                        light_install=light_install)
      self.tic()

    def uninstallBusinessTemplate(self, *template_list):
      template_list = set(template_list)
      uninstalled_list = []
      portal = self.portal
      for bt in portal.portal_templates.getInstalledBusinessTemplateList():
        bt_title = bt.getTitle()
        if bt_title in template_list:
          bt.uninstall(remove_translations=True)
          uninstalled_list.append(bt_title)
      if uninstalled_list:
        getattr(portal, 'ERP5Site_updateTranslationTable', lambda: None)()
      self.tic()
      return uninstalled_list

    def setUp(self):
      '''Sets up the fixture. Do not override,
         use the hooks instead.
      '''
      from Products.CMFActivity.ActivityRuntimeEnvironment import BaseMessage
      # Activities in unit tests shall never fail.
      # Let's be a litte tolerant for the moment.
      BaseMessage.max_retry = property(lambda self:
        self.activity_kw.get('max_retry', 1))

      template_list = list(self.getBusinessTemplateList())
      erp5_catalog_storage = os.environ.get('erp5_catalog_storage',
                                            'erp5_mysql_innodb_catalog')
      update_business_templates = os.environ.get('update_business_templates') is not None
      erp5_load_data_fs = int(os.environ.get('erp5_load_data_fs', 0))
      if update_business_templates and erp5_load_data_fs:
        update_only = os.environ.get('update_only', None)
        template_list[:0] = (erp5_catalog_storage, 'erp5_property_sheets',
                             'erp5_core', 'erp5_xhtml_style')
        # Update only specified business templates, regular expression
        # can be used.
        if update_only is not None:
          update_only_list = update_only.split(',')
          matching_template_list = []
          # First parse the template list in order to keep same order
          for business_template in template_list:
            for expression in update_only_list:
              if re.search(expression, business_template):
                matching_template_list.append(business_template)
          template_list = matching_template_list

      # keep a mapping type info name -> property sheet list, to remove them in
      # tear down.
      self._added_property_sheets = {}
      light_install = self.enableLightInstall()
      create_activities = self.enableActivityTool()
      hot_reindexing = self.enableHotReindexing()
      for x, y in (("erp5_core_proxy_field_legacy", "erp5_base"),
                   ("erp5_stock_cache", "erp5_pdm")):
        if x not in template_list:
          try:
            template_list.insert(template_list.index(y), x)
          except ValueError:
            pass
      self.setUpERP5Site(business_template_list=template_list,
                         light_install=light_install,
                         create_activities=create_activities,
                         quiet=install_bt5_quiet,
                         hot_reindexing=hot_reindexing,
                         erp5_catalog_storage=erp5_catalog_storage)
      PortalTestCase.setUp(self)

    def afterSetUp(self):
      '''Called after setUp() has completed. This is
         far and away the most useful hook.
      '''
      pass

    def getBusinessTemplateList(self):
      """
        You must override this. Return the list of business templates.
      """
      return ()

    def loadPromise(self):
      """ Create promise configuration file and load it into configuration
      """
      promise_path = os.path.join(instancehome, "promise.cfg")
      ZopeTestCase._print('Adding Promise at %s...\n' % promise_path)
      _createTestPromiseConfigurationFile(promise_path)
      config.product_config["/%s" % self.getPortalName()] = \
         {"promise_path": promise_path}

    def _updateConnectionStrings(self):
      """Update connection strings with values passed by the testRunner
      """
      # update connection strings
      for connection_string_name, connection_string in\
                                    _getConnectionStringDict().items():
        connection_name = connection_string_name.replace('_string', '')
        getattr(self.portal, connection_name).edit('', connection_string)

    def _updateConversionServerConfiguration(self):
      """Update conversion server (Oood) at default site preferences.
      """
      conversion_dict = _getConversionServerDict()
      preference = self.portal.portal_preferences[
                        self.getDefaultSitePreferenceId()]
      preference._setPreferredOoodocServerAddress(conversion_dict['hostname'])
      preference._setPreferredOoodocServerPortNumber(conversion_dict['port'])

    def _updateMemcachedConfiguration(self):
      """Update default memcached plugin configuration
      """
      portal_memcached = self.portal.portal_memcached
      connection_dict = _getVolatileMemcachedServerDict()
      url_string = '%(hostname)s:%(port)s' % connection_dict
      if portal_memcached.default_memcached_plugin.getUrlString() != url_string:
        portal_memcached.default_memcached_plugin.setUrlString(url_string)

    def _recreateCatalog(self, quiet=0):
      """Clear activities and catalog and recatalog everything.
      Test runner can set `erp5_tests_recreate_catalog` environnement variable,
      in that case we have to clear catalog. """
      if int(os.environ.get('erp5_tests_recreate_catalog', 0)):
        try:
          _start = time.time()
          if not quiet:
            ZopeTestCase._print('\nRecreating catalog ... ')
          portal = self.getPortal()
          portal.portal_activities.manageClearActivities()
          portal.portal_catalog.manage_catalogClear()
          self.commit()
          portal.ERP5Site_reindexAll()
          self.tic()
          if not quiet:
            ZopeTestCase._print('done (%.3fs)\n' % (time.time() - _start,))
        finally:
          os.environ['erp5_tests_recreate_catalog'] = '0'

    def _installBusinessTemplateList(self, business_template_list,
                                     light_install=True,
                                     quiet=True):
      template_tool = self.portal.portal_templates
      update_business_templates = os.environ.get('update_business_templates') is not None
      BusinessTemplate_getModifiedObject = aq_base(
        getattr(self.portal, 'BusinessTemplate_getModifiedObject', None))

      # Add some business templates
      for url, bt_title in business_template_list:
        start = time.time()
        get_install_kw = False
        if bt_title in template_tool.getInstalledBusinessTemplateTitleList():
          if update_business_templates:
            if not quiet:
              ZopeTestCase._print('Updating %s business template ... ' % bt_title)
            if BusinessTemplate_getModifiedObject is not None:
              get_install_kw = True
          else:
            continue
        else:
          if not quiet:
            ZopeTestCase._print('Adding %s business template ... ' % bt_title)
        bt = template_tool.download(url)
        if not quiet:
          ZopeTestCase._print('(imported in %.3fs) ' % (time.time() - start))
          # For unit test, we accept installing business templates with
          # missing a part of dependencies.
          missing_dep_list = bt.getMissingDependencyList()
          if len(missing_dep_list) > 0:
            ZopeTestCase._print('(missing dependencies : %r) ' % missing_dep_list)
        install_kw = None
        if get_install_kw:
          install_kw = {}
          listbox_object_list = BusinessTemplate_getModifiedObject.__of__(bt)()
          for listbox_line in listbox_object_list:
            install_kw[listbox_line.object_id] = listbox_line.choice_item_list[0][1]
        bt.install(light_install=light_install,
                   object_to_update=install_kw,
                   update_catalog=bt.isCatalogUpdatable(),
                   update_translation=1)
        # Release locks
        self.commit()
        if not quiet:
          ZopeTestCase._print('done (%.3fs)\n' % (time.time() - start))

    def setUpERP5Site(self,
                     business_template_list=(),
                     quiet=0,
                     light_install=1,
                     create_activities=1,
                     hot_reindexing=1,
                     erp5_catalog_storage='erp5_mysql_innodb_catalog'):
      '''
        Creates an ERP5 site.
        business_template_list must be specified correctly
        (e.g. '("erp5_base", )').
      '''
      portal_name = self.getPortalName()
      title = self.getTitle()
      if portal_name in failed_portal_installation:
        raise SetupSiteError(
            'Installation of %s already failed, giving up' % portal_name)
      try:
        self.app = app = self._app()
        app.test_portal_name = portal_name

        global setup_done
        setup_key = (portal_name,) + tuple(business_template_list)
        if setup_key not in setup_done:
          setup_done.add(setup_key)
          business_template_list = \
            self._getBTPathAndIdList(business_template_list)
          try:
            _start = time.time()
            # Add user and log in
            if not quiet:
              ZopeTestCase._print('Adding ERP5TypeTestCase user ...\n')
            uf = app.acl_users
            uf._doAddUser('ERP5TypeTestCase', '', ['Manager', 'Member', 'Assignee',
                          'Assignor', 'Author', 'Auditor', 'Associate'], [])
            user = uf.getUserById('ERP5TypeTestCase').__of__(uf)
            newSecurityManager(None, user)

            # bt5s contain ZODB Components which can be only installed if the
            # user has Developer Role
            addUserToDeveloperRole('ERP5TypeTestCase')

            # Add ERP5 Site
            reindex = 1
            if hot_reindexing:
              setattr(app, 'isIndexable', 0)
              reindex = 0

            if app._getOb(portal_name, None) is None:
              if not quiet:
                ZopeTestCase._print('Adding %s ERP5 Site ... ' % portal_name)

              extra_constructor_kw = _getConnectionStringDict()
              # manage_addERP5Site does not accept the following 2 arguments
              for k in ('erp5_sql_deferred_connection_string',
                        'erp5_sql_transactionless_connection_string'):
                extra_constructor_kw.pop(k, None)
              email_from_address = os.environ.get('email_from_address')
              if email_from_address is not None:
                extra_constructor_kw['email_from_address'] = email_from_address

              factory = app.manage_addProduct['ERP5']
              factory.manage_addERP5Site(portal_name,
                                       erp5_catalog_storage=erp5_catalog_storage,
                                       light_install=light_install,
                                       reindex=reindex,
                                       create_activities=create_activities,
                                       **extra_constructor_kw )
              sql = extra_constructor_kw.get('erp5_sql_connection_string')
              if sql:
                app[portal_name]._setProperty('erp5_site_global_id',
                                              base64.standard_b64encode(sql))
              if not quiet:
                ZopeTestCase._print('done (%.3fs)\n' % (time.time() - _start))
              # Release locks
              self.commit()
            self.portal = portal = self.getPortal()

            if len(setup_done) == 1: # make sure it is run only once
              self._setUpDummyMailHost()
              self.startZServer(verbose=True)
              self._registerNode(distributing=1, processing=1)
              self.loadPromise()

            self._updateConnectionStrings()
            self._recreateCatalog()
            self._installBusinessTemplateList(business_template_list,
                                              light_install=light_install,
                                              quiet=quiet)
            self._updateConversionServerConfiguration()
            self._updateMemcachedConfiguration()
            # Create a Manager user at the Portal level
            uf = self.getPortal().acl_users
            uf._doAddUser('ERP5TypeTestCase', '', ['Manager', 'Member', 'Assignee',
                            'Assignor', 'Author', 'Auditor', 'Associate'], [])
            user = uf.getUserById('ERP5TypeTestCase').__of__(uf)

            self._callSetUpOnce()

            # Enable reindexing
            # Do hot reindexing # Does not work
            if hot_reindexing:
              setattr(app,'isIndexable', 1)
              portal.portal_catalog.manage_hotReindexAll()

            portal.portal_types.resetDynamicDocumentsOnceAtTransactionBoundary()
            self.tic(not quiet)

            # Log out
            if not quiet:
              ZopeTestCase._print('Logout ... \n')
            noSecurityManager()
            if not quiet:
              ZopeTestCase._print('done (%.3fs)\n' % (time.time()-_start,))
              ZopeTestCase._print('Running Unit tests of %s\n' % title)
          except:
            self.abort()
            raise
          else:
            self.commit()
            del self.portal, self.app
            ZopeTestCase.close(app)
      except:
        ZopeTestCase._print(traceback.format_exc())
        failed_portal_installation[portal_name] = 1
        ZopeTestCase._print('Ran Unit test of %s (installation failed)\n'
                            % title) # run_unit_test depends on this string.
        raise

    def afterClear(self):
      '''Called after the fixture has been cleared.
         Note that this may occur during setUp() *and*
         tearDown().
      '''
      setSite() # undo site configuration from self.getPortal()

    def tearDown(self):
      '''Tears down the fixture. Do not override,
         use the hooks instead.
      '''
      if not int(os.environ.get('erp5_save_data_fs', 0)):
        # Drop remaining activities if some of them failed.
        # However, we should not do more activity cleaning, because properly
        # written unit tests should not leave unprocessed activity messages.
        # And the user may want to analyse the result of a failed unit test,
        # so we do nothing in persistent mode (--save).
        try:
          portal_activities = self.portal.portal_activities
          message_list = portal_activities.getMessageList()
        except StandardError: # AttributeError, TransactionFailedError ...
          pass
        else:
          for m in message_list:
            if m.processing_node < -1:
              self.abort()
              count = portal_activities.countMessage()
              portal_activities.manageClearActivities()
              self.commit()
              ZopeTestCase._print(' (dropped %d left-over activity messages) '
                                  % count)
              break
      PortalTestCase.tearDown(self)

    def importObjectFromFile(self, container, relative_path, **kw):
      """Import an object from a file located in $TESTFILEDIR/input/"""
      test_path = os.path.dirname(__file__)
      source_path = os.path.join(test_path, 'input', relative_path)
      assert os.path.exists(source_path)
      obj = container._importObjectFromFile(source_path, **kw)
      obj.manage_afterClone(obj)
      return obj

class ERP5TypeTestCase(ERP5TypeCommandLineTestCase):
    """TestCase for ERP5 based tests.

    This TestCase setups an ERP5Site and installs business templates.
    """

from Products.ERP5 import ERP5Site
ERP5Site.getBootstrapBusinessTemplateUrl = lambda bt_title: \
  ERP5TypeCommandLineTestCase._getBTPathAndIdList((bt_title,))[0][0]


class ResponseWrapper:
    '''Decorates a response object with additional introspective methods.'''

    _headers_separator_re = re.compile('(?:\r?\n){2}')

    def __init__(self, response, outstream, path):
        self._response = response
        self._outstream = outstream
        self._path = path

    def __getattr__(self, name):
        return getattr(self._response, name)

    def getOutput(self):
        '''Returns the complete output, headers and all.'''
        return self._outstream.getvalue()

    def getBody(self):
        '''Returns the page body, i.e. the output par headers.'''
        output = self.getOutput()
        try:
            headers, body = self._headers_separator_re.split(output, 1)
            return body
        except ValueError:
            # not enough values to unpack: no body
            return None

    def getPath(self):
        '''Returns the path used by the request.'''
        return self._path

    def getHeader(self, name):
        '''Returns the value of a response header.'''
        return self.headers.get(name.lower())

    def getCookie(self, name):
        '''Returns a response cookie.'''
        return self.cookies.get(name)

class ERP5ReportTestCase(ERP5TypeTestCase):
  """Base class for testing ERP5 Reports
  """
  def getReportSectionList(self, context, report_name):
    """Get the list of report sections in a report called on context."""
    report = getattr(context, report_name)
    report_method = getattr(report, 'report_method', None)
    if report_method:
      return getattr(context, report_method)()
    return sum([list(field.render())
                for field in report.get_fields()
                if field.getRecursiveTemplateField().meta_type == 'ReportBox'],
               [])

  def getListBoxLineList(self, report_section):
    """Render the listbox in a report section, return None if no listbox exists
    in the report_section.
    """
    result = None
    here = report_section.getObject(self.portal)
    report_section.pushReport(self.portal)
    form = getattr(here, report_section.getFormId())
    self.portal.REQUEST['here'] = here
    if form.has_field('listbox'):
      result = form.listbox.get_value('default',
                                      render_format='list',
                                      REQUEST=self.portal.REQUEST)
    report_section.popReport(self.portal)
    return result

  def checkLineProperties(self, line, **kw):
    """Check properties of a report line.
    """
    diff_list = []
    for k, v in kw.items():
      if v != line.getColumnProperty(k):
        diff_list.append('`%s`: expected: %r actual: %r' %
                                (k, v, line.getColumnProperty(k)))
    if diff_list:
      self.fail('Lines differs:\n' + '\n'.join(diff_list))

def dummy_setUp(self):
  '''
  This one is overloaded so that it does not execute beforeSetUp and afterSetUp
  from the original tests, which would write to the FileStorage when --save is
  enabled
  '''
  try:
      self.beforeSetUp()
      self.app = self._app()
      self.portal = self._portal()
      self._setup()
  except:
      self._clear()
      raise

def dummy_tearDown(self):
  '''
  This one is overloaded so that it does not execute beforeTearDown from
  the original tests, which would write to the FileStorage when --save
  is enabled
  '''
  self._clear(1)

class ZEOServerTestCase(ERP5TypeTestCase):
  """TestCase class to run a ZEO storage

  Main method is 'asyncore_loop' (inherited) since there is nothing to do
  except processing I/O.
  """

  def setUp(self):
    # Start ZEO storage and send address to parent process if any.
    from Zope2.custom_zodb import zeo_client, Storage
    from ZEO.StorageServer import StorageServer
    storage = {'1': Storage}
    for host_port in parseListeningAddress(os.environ.get('zeo_server')):
      try:
        self.zeo_server = StorageServer(host_port, storage)
        break
      except socket.error, e:
        if e[0] != errno.EADDRINUSE:
          raise
    if zeo_client:
      os.write(zeo_client, repr(host_port))
      os.close(zeo_client)
    ZopeTestCase._print("\nZEO Storage started at %s:%s ... " % host_port)

  def tearDown(self):
    self.zeo_server.close_server()


class lazy_func_prop(object):
  """Descriptor to delay the compilations of Python Scripts
     until some of their attributes are accessed.
  """
  default_dict = {}
  def __init__(self, name, default):
    self.name = name
    self.default_dict[name] = default
  def __get__(self, instance, owner):
    if self.name not in instance.__dict__:
      instance.__dict__.update(self.default_dict)
      instance._orig_compile()
    return instance.__dict__[self.name]
  def __set__(self, instance, value):
    instance.__dict__[self.name] = value
  def __delete__(self, instance):
    del instance.__dict__[self.name]

@onsetup
def optimize():
  '''Significantly reduces portal creation time.'''
  def __init__(self, text):
    # Don't compile expressions on creation
    self.text = text
  from Products.CMFCore.Expression import Expression
  Expression.__init__ = __init__

  # Delay the compilations of Python Scripts until they are really executed.
  from Products.PythonScripts.PythonScript import PythonScript
  # Python Scripts are exported without those 2 attributes:
  PythonScript.func_code = lazy_func_prop('func_code', None)
  PythonScript.func_defaults = lazy_func_prop('func_defaults', None)

  PythonScript._orig_compile = PythonScript._compile
  def _compile(self):
    # mark the script as being not compiled
    for name in lazy_func_prop.default_dict:
      self.__dict__.pop(name, None)
  PythonScript._compile = _compile
  PythonScript_exec = PythonScript._exec
  def _exec(self, *args):
    self.func_code # trigger compilation if needed
    return PythonScript_exec(self, *args)
  PythonScript._exec = _exec
  from Acquisition import aq_parent
  def _makeFunction(self, dummy=0): # CMFCore.FSPythonScript uses dummy arg.
    self.ZCacheable_invalidate()
    self.__dict__.update(lazy_func_prop.default_dict)
    self._orig_compile()
    if not (aq_parent(self) is None or hasattr(self, '_filepath')):
      # It needs a _filepath, and has an acquisition wrapper.
      self._filepath = self.get_filepath()
  PythonScript._makeFunction = _makeFunction

  # Do not reindex portal types sub objects by default
  # We will probably disable reindexing for other types later
  full_indexing_set = set(os.environ.get('enable_full_indexing', '').split(','))
  if not 'portal_types' in full_indexing_set:
    from Products.ERP5Type.Core.ActionInformation import ActionInformation
    from Products.ERP5Type.Core.RoleInformation import RoleInformation
    ActionInformation.isIndexable = RoleInformation.isIndexable = \
      ConstantGetter('isIndexable', value=False)
  if not 'portal_property_sheets' in full_indexing_set:
    from Products.ERP5Type.Core.StandardProperty import StandardProperty
    from Products.ERP5Type.Core.CategoryProperty import CategoryProperty
    from Products.ERP5Type.mixin.constraint import ConstraintMixin
    StandardProperty.isIndexable = CategoryProperty.isIndexable = \
      ConstraintMixin.isIndexable = ConstantGetter('isIndexable', value=False)

optimize()

@onsetup
def fortify():
  '''Add some extra checks that we don't have at runtime, not to slow down the
  system.
  '''
  # check that we don't store persistent objects in cache
  from Products.ERP5Type.CachePlugins.BaseCache import CacheEntry
  CacheEntry.__original_init__ = CacheEntry.__init__
  def __init__(self, value, *args, **kw):
    # this will raise TypeError if you try to cache a persistent object
    dumps(value)
    return self.__original_init__(value, *args, **kw)
  CacheEntry.__init__ = __init__

  # randomize priorities of activities in a deterministic way
  seed = os.environ.get("random_activity_priority")
  if seed is not None:
    ZopeTestCase._print("RNG seed for priorities of activities is %r\n" % seed)
    rng = random.Random(seed)
    from Products.CMFActivity.ActivityTool import Message
    Message__init__ = Message.__init__
    def __init__(self, url, oid, active_process, active_process_uid,
                 activity_kw, *args, **kw):
      activity_kw['priority'] = rng.randint(-128, 127)
      Message__init__(self, url, oid, active_process, active_process_uid,
                      activity_kw, *args, **kw)
    Message.__init__ = __init__


fortify()
