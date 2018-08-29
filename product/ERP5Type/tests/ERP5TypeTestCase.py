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
import string
import sys
import time
import traceback
import urllib
import ConfigParser
from contextlib import contextmanager
from io import BytesIO
from functools import partial
from six.moves.urllib.parse import unquote_to_bytes
from cPickle import dumps
from glob import glob
from hashlib import md5
from warnings import warn
from DateTime import DateTime
import mock
import Products.ZMySQLDA.DA
from Products.ZMySQLDA.DA import Connection as ZMySQLDA_Connection
from zope.globalrequest import clearRequest
from zope.globalrequest import getRequest
from zope.globalrequest import setRequest
import six

from zope.component.hooks import setSite

from Testing import ZopeTestCase
from Testing.makerequest import makerequest
from Testing.ZopeTestCase import connections, PortalTestCase, user_name, ZopeLite, functional
from Products.ERP5Type.Core.Workflow import ValidationFailed
from Products.PythonScripts.PythonScript import PythonScript
from Products.ERP5Type.Accessor.Constant import PropertyGetter as ConstantGetter
from Products.ERP5Form.PreferenceTool import Priority
from zLOG import LOG, DEBUG
from Products.ERP5Type.Utils import convertToUpperCase, str2bytes
from Products.ERP5Type.tests.backportUnittest import SetupSiteError
from Products.ERP5Type.tests.utils import addUserToDeveloperRole
from Products.ERP5Type.tests.utils import parseListeningAddress
from Products.ERP5Type.tests.utils import timeZoneContext

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

from Products.ERP5Type.tests.ProcessingNodeTestCase import \
  ProcessingNodeTestCase, patchActivityTool
onsetup(patchActivityTool)()

from AccessControl.SecurityManagement import newSecurityManager, noSecurityManager
from Products.ZSQLCatalog.SQLCatalog import Query

from Acquisition import aq_base

if six.PY2:
  from contextlib import contextmanager
  @contextmanager
  def nullcontext(enter_result=None):
      yield enter_result
else:
  from contextlib import nullcontext


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

def _getConversionServerUrlList():
  """ Return the url for Conversion Server (Cloudooo)
  """
  url = os.environ.get('conversion_server_url')
  if not url: # BBB
    url = os.environ['conversion_server_url'] = 'http://%s:%s' % (
      os.environ.get('conversion_server_hostname', 'localhost'),
      os.environ.get('conversion_server_port', 8008))
    warn('conversion_server_hostname/conversion_server_port are deprecated.\n'
      'Using %s as conversion_server_url instead' % url, DeprecationWarning)
  return url.split(',')

def _getConversionServerRetryCount():
  """ Return retry count for Conversion Server (Cloudooo)
  """
  return os.environ.get('conversion_server_retry_count', 2)

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

def _createTestPromiseConfigurationFile(promise_path, bt5_repository_path_list=None):
  kumofs_url = "memcached://%(hostname)s:%(port)s/" % \
                             _getPersistentMemcachedServerDict()
  memcached_url = "memcached://%(hostname)s:%(port)s/" % \
                             _getVolatileMemcachedServerDict()
  cloudooo_url_list = _getConversionServerUrlList()

  promise_config = ConfigParser.RawConfigParser()
  promise_config.add_section('external_service')
  promise_config.set('external_service', 'cloudooo_url_list', cloudooo_url_list)
  promise_config.set('external_service', 'memcached_url',memcached_url)
  promise_config.set('external_service', 'kumofs_url', kumofs_url)

  if bt5_repository_path_list is not None:
    promise_config.add_section('portal_templates')
    promise_config.set('portal_templates', 'repository',
                                   ' '.join(bt5_repository_path_list))

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


class ERP5TypeTestCaseRequestConnection(object):
  """A "Connection" to ensure the test runs with an independent request
  and that the original request is properly restored at the end of test.

  This is used with Testing.ZopeTestCase.connection.registry
  """
  def __init__(self, request):
    self._current_request = getRequest()
    setRequest(request)

  def close(self):
    setRequest(self._current_request)


class ERP5TypeTestCaseMixin(ProcessingNodeTestCase, PortalTestCase, functional.Functional):
    """Mixin class for ERP5 based tests.
    """
    manager_username = 'ERP5TypeTestCase'
    manager_password = None  # will be generated at setup

    def __init__(self, *args, **kw):
      super(ERP5TypeTestCaseMixin, self).__init__(*args, **kw)
      self.sequence_string_registry = {}

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

    def setUpManagerUser(self, quiet=False):
      """Adds default manager user with all roles.
      """
      self._setUpManagerPassword()
      uf = self.portal.acl_users
      user = uf.getUser(self.manager_username)
      if user is not None:
        uf.zodb_users.removeUser(self.manager_username)

      self._addUserWithAllRoles(
        user_folder=uf,
        username=self.manager_username,
        password=self.manager_password,
      )
      if not quiet:
        ZopeTestCase._print(
          'Added %s user with password %s ...\n' % (
            self.manager_username, self.manager_password))

    def _setUpManagerPassword(self):
      if self.manager_password is None:
        ERP5TypeTestCaseMixin.manager_password = self.newPassword()

    def _addUserWithAllRoles(self, user_folder, username, password):
      """Adds a user with all roles.
      """
      assert user_folder._doAddUser(username, password, ['Manager', 'Member', 'Assignee',
                    'Assignor', 'Author', 'Auditor', 'Associate'], [])

    def newPassword(self):
      """ Generate a password """
      return ''.join(random.SystemRandom().sample(string.ascii_letters + string.digits, 20))

    def login(self, user_name='ERP5TypeTestCase', quiet=0):
      """
      Most of the time, we need to login before doing anything

      ATTENTION: user_name argument in this method is user's ID in
      reality. If you want to login by user_name, use loginByUserName()
      instead.
      """
      return PortalTestCase.login(self, user_name)

    def loginByUserName(self, user_name='ERP5TypeTestCase', quiet=0):
      """
      Most of the time, we need to login before doing anything
      """
      uf = self.portal.acl_users
      user = uf.getUser(user_name)
      if not hasattr(user, 'aq_base'):
        user = user.__of__(uf)
      newSecurityManager(None, user)

    def whoami(self):
      """
      Returns username of currently logged in user
      """
      self.portal.portal_membership.getAuthenticatedMember().getUserName()

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
      self.portal.ERP5Site_updateTranslationTable()
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

    def changeSkin(self, skin_name):
      """
        Change current Skin
      """
      request = self.app.REQUEST
      self.portal.portal_skins.changeSkin(skin_name)
      request.set('portal_skin', skin_name)

    def logout(self):
      PortalTestCase.logout(self)
      # clean up certain cache related REQUEST keys that might be associated
      # with the logged in user
      if getattr(self, 'REQUEST', None) is not None:
        for key in ('_ec_cache', '_oai_cache'):
          self.REQUEST.other.pop(key, None)

    def _setupUser(self):
      '''Creates the default member user (for PortalTestCase).'''
      uf = self.portal.acl_users
      # do nothing if the user already exists
      if not uf.getUserById(user_name):
        uf._doAddUser(user_name, self.newPassword(), ['Member'], [])

    def pinDateTime(self, date_time):
      # pretend time has stopped at a certain date (i.e. the test runs
      # infinitely fast), for example to avoid errors on tests that are started
      # just before midnight.
      # This can be used as a context manager, otherwise use unpinDateTime to
      # reset.
      global _pinned_date_time
      assert date_time is None or isinstance(date_time, DateTime)
      _pinned_date_time = date_time

      unpinDateTime = self.unpinDateTime
      class UnpinContextManager(object):
        def __enter__(self):
          return self
        def __exit__(self, *args):
          unpinDateTime()
      return UnpinContextManager()

    def unpinDateTime(self):
      self.pinDateTime(None)

    def setTimeZoneToUTC(self):
      # Deprecated, prefer using `timeZoneContext` context manager instead.
      timezone = timeZoneContext('UTC')
      timezone.__enter__()
      self.addCleanup(timezone.__exit__, None, None, None)

    def getDefaultSystemPreference(self):
      id = 'default_system_preference'
      tool = self.getPreferenceTool()
      try:
        pref = tool[id]
      except KeyError:
        pref = tool.newContent(id, 'System Preference')
        pref.setPriority(Priority.SITE)
        pref.enable()
      return pref

    # Utility methods specific to ERP5Type
    def getTemplateTool(self):
      return getattr(self.portal, 'portal_templates', None)

    def getPreferenceTool(self) :
      return getattr(self.portal, 'portal_preferences', None)

    def getTrashTool(self):
      return getattr(self.portal, 'portal_trash', None)

    def getPasswordTool(self):
      return getattr(self.portal, 'portal_password', None)

    def getSkinsTool(self):
      return getattr(self.portal, 'portal_skins', None)

    def getCategoryTool(self):
      return getattr(self.portal, 'portal_categories', None)

    def getWorkflowTool(self):
      return getattr(self.portal, 'portal_workflow', None)

    def getCatalogTool(self):
      return getattr(self.portal, 'portal_catalog', None)

    def getTypesTool(self):
      return getattr(self.portal, 'portal_types', None)
    getTypeTool = getTypesTool

    def getRuleTool(self):
      return getattr(self.portal, 'portal_rules', None)

    def getSimulationTool(self):
      return getattr(self.portal, 'portal_simulation', None)

    def getSQLConnection(self):
      return getattr(self.portal, 'erp5_sql_connection', None)

    def getPortalId(self):
      return self.portal.getId()

    def getDomainTool(self):
      return getattr(self.portal, 'portal_domains', None)

    def getAlarmTool(self):
      return getattr(self.portal, 'portal_alarms', None)

    def getActivityTool(self):
      return getattr(self.portal, 'portal_activities', None)

    def getArchiveTool(self):
      return getattr(self.portal, 'portal_archives', None)

    def getCacheTool(self):
      return getattr(self.portal, 'portal_caches', None)

    def getOrganisationModule(self):
      return getattr(self.portal, 'organisation_module',
          getattr(self.portal, 'organisation', None))

    def getPersonModule(self):
      return getattr(self.portal, 'person_module',
          getattr(self.portal, 'person', None))

    def getCurrencyModule(self):
      return getattr(self.portal, 'currency_module',
          getattr(self.portal, 'currency', None))

    def getCreatedTypeList(self, portal_type, from_date=None):
      """
      Convenient method to retrieve new documents created in the testn in
      particular documents that are created indirectly, like trough activities.
      "begin" attribute of test class instance could be initialized in an
      afterSetup.
      """
      if from_date is None:
        from_date = getattr(self, 'begin')
      type_list = [x.getObject() for x in self.portal.portal_catalog(
                  portal_type=portal_type,
                  query=Query(creation_date=from_date, range="min"))]
      type_list.sort(key=lambda x: x.getCreationDate())
      return type_list

    def checkPropertyConstraint(self, document, property_name, value,
                                decreased_quantity=1, commit=False):
      """
      Convenient method to check required properties on documents. It check that
      number of consistency errors decrease when property is set
      """
      document.setProperty(property_name, None)
      initial_consistency_len = len(document.checkConsistency())
      document.setProperty(property_name, value)
      if commit:
        self.commit()
      self.assertEqual(len(document.checkConsistency()),
                           initial_consistency_len-decreased_quantity)

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
      if getattr(self, '_added_property_sheets', None) is None:
        self._added_property_sheets = {}
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
        User password is randomly generated.
      """
      user = self.createUser(reference, person_kw=dict(title=title))
      assignment = self.createUserAssignment(user, assignment_kw=dict(function=function))
      return user

    def createUser(self, reference, password=None, person_kw=None):
      """
        Create an ERP5 User.
        Default password is randomly generated.
        person_kw is passed as additional arguments when creating the person
      """
      if password is None:
        password = self.newPassword()
      if person_kw is None:
        person_kw = {}

      person = self.portal.person_module.newContent(portal_type='Person',
                                                    reference=reference,
                                                    **person_kw)
      login = person.newContent(portal_type='ERP5 Login',
                                reference=reference,
                                password=password)
      login.validate()
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
      bt5_path_list = os.environ['erp5_tests_bt5_path'].split(',')
      bt5_path_list += [os.path.join(path, "*") for path in bt5_path_list]

      def search(path, template):
        path_list = glob(os.path.join(path, template))
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

    def _getBusinessRepositoryPathList(self, searchable_business_template_list=None):
      if searchable_business_template_list is None:
        searchable_business_template_list = ["erp5_base"]

      template_list = []
      for bt_id in searchable_business_template_list:
        bt_template_list = self._getBTPathAndIdList([bt_id])
        if len(bt_template_list):
          template_list.append(bt_template_list[0])

      if len(template_list) > 0:
        return ["/".join(x[0].split("/")[:-1]) for x in template_list]

      return []

    def setupAutomaticBusinessTemplateRepository(self, accept_public=True,
                              searchable_business_template_list=("erp5_base",)):
      template_tool = self.portal.portal_templates
      bt_set = set(searchable_business_template_list).difference(x['title']
        for x in six.itervalues(template_tool.repository_dict) for x in x)
      if bt_set:
        template_tool.updateRepositoryBusinessTemplateList(
          {os.path.dirname(x[0]) for x in self._getBTPathAndIdList(bt_set)},
          genbt5list=1)

    def assertSameSet(self, a, b, msg=None):
      """deprecated, please use assertEqual(set(a), set(b))
      """
      self.assertEqual(set(a), set(b), msg)
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
      ZopeTestCase._print('\n%s' % message)
      LOG('Testing ... ', DEBUG, message)

    def publish(self, path, basic=None, env=None, extra=None,
                request_method='GET', stdin=None, handle_errors=True,
                user=None):
      '''Publishes the object at 'path' returning a response object.

      This is from Testing.ZopeTestCase.Functional, extended to support passing
      a user id directly.
      '''
      if user:
        assert not basic
        from six.moves._thread import get_ident
        me = get_ident()
        def _extractUserIds(pas, request, plugins):
          if me == get_ident():
            info = pas._verifyUser(plugins, user)
            return [(info['id'], info['login'])] if info else ()
          return mock.DEFAULT
        user_context = mock.patch(
          'Products.PluggableAuthService.PluggableAuthService.PluggableAuthService._extractUserIds',
          side_effect=_extractUserIds,
          autospec=True)
      else:
         user_context = nullcontext()

      request = getRequest()
      try:
        with user_context:
          return super(ERP5TypeTestCaseMixin, self).publish(
            path,
            basic=basic,
            env=env,
            extra=extra,
            request_method=request_method,
            stdin=stdin,
            handle_errors=handle_errors,
          )
      finally:
        # Make sure that the skin cache does not have objects that were
        # loaded with the connection used by the requested url.
        self.changeSkin(self.portal.getCurrentSkinName())
        setRequest(request)

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

    def _getCleanupDict(self):
      """
        You must override this. Return the documents that should be
        stored while saving/restoring a StoredSequence as a dict,
        the keys being the module containing them, and the values
        the list of ids of documents
      """
      return {}

    def registerSequenceString(self, sequence_title, sequence_string):
      self.sequence_string_registry[sequence_title] = sequence_string

    def getSequenceString(self, sequence_title):
      return self.sequence_string_registry[sequence_title]

    def stepStoreSequence(self, sequence):
      sequence_title = "sequence_title"
      document_dict = self._getCleanupDict()
      if sequence_title in self.portal.portal_trash:
        self.portal.portal_trash.manage_delObjects(ids=[sequence_title])
      trashbin_value = self.portal.portal_trash.newContent(
        portal_type="Trash Bin",
        id=sequence_title,
        title=sequence_title,
        serialized_sequence=sequence.serializeSequenceDict(),
        document_dict=document_dict,
      )
      for module_id, object_id_list in six.iteritems(document_dict):
        for object_id in object_id_list:
          self.portal.portal_trash.backupObject(
            trashbin_value, [module_id], object_id, save=True, keep_subobjects=True
          )

    def stepRestoreSequence(self, sequence):
      sequence_title = "sequence_title"
      trashbin_value = self.portal.portal_trash[sequence_title]
      document_dict = trashbin_value.getProperty('document_dict')
      for module_id, object_id_list in six.iteritems(document_dict):
        for object_id in object_id_list:
          self.portal.portal_trash.restoreObject(
            trashbin_value, [module_id], object_id, pass_if_exist=True
          )
      sequence.deserializeSequenceDict(
        trashbin_value.getProperty("serialized_sequence"),
      )
      self.tic()

    def setDocumentOwner(self, document_value, user):
      """
      Change both ownership and Owner local role on given document to given
      user.
      """
      try:
        _, old_owner_user_id = document_value.getOwnerTuple()
      except ValueError:
        pass
      else:
        old_owner_local_role_set = list(document_value.get_local_roles_for_userid(
          old_owner_user_id,
        ))
        try:
          old_owner_local_role_set.remove('Owner')
        except ValueError:
          pass
        else:
          if old_owner_local_role_set:
            document_value.manage_setLocalRoles(
              old_owner_user_id,
              tuple(old_owner_local_role_set),
            )
          else:
            document_value.manage_delLocalRoles(old_owner_user_id)
      document_value.changeOwnership(user)
      user_id = user.getId()
      document_value.manage_setLocalRoles(
        user_id,
        document_value.get_local_roles_for_userid(user_id) + ('Owner', ),
      )
      document_value.reindexObject()

    def immediateRecursiveCall(self, document_value, callback):
      """
      Call given callback on document and all its subdocuments.

      Obviously not scalable to large document trees (and hence is only in
      tests and not in the regular ERP5 document API).
      """
      stack = [document_value]
      while stack:
        document_value = stack.pop()
        callback(document_value)
        stack.extend(getattr(document_value, 'objectValues', lambda: ())())
        stack.extend(getattr(document_value, 'opaqueValues', lambda: ())())

    def setSubtreeOwner(self, document_value, user):
      """
      Change owner of document_value and all its subdocuments to user.
      See also setDocumentOwner.
      """
      setDocumentOwner = self.setDocumentOwner
      self.immediateRecursiveCall(
        document_value=document_value,
        callback=lambda document_value: setDocumentOwner(
          document_value=document_value,
          user=user,
        ),
      )

class ERP5TypeCommandLineTestCase(ERP5TypeTestCaseMixin):
    __original_ZMySQLDA_connect = None

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

      We override this method so that the request knows about the address of
      our http server and also to set HTTP_ACCEPT_CHARSET set in REQUEST, to
      get the zpt unicode conflict resolver to
      work properly.

      We reimplement PortalTestCase._app instead of calling it, because it
      opens a ZODB connection and wrap the root object a request to
      http://nohost, but we prefer to create directly a connection to the
      app wrapped in a request to our web server.
      '''
      if hasattr(self, 'app'):
        return self.app
      app = ZopeLite.app()
      environ = {}
      if self._server_address:
        host, port = self._server_address
        environ['SERVER_NAME'] = host
        environ['SERVER_PORT'] = str(port)

      app = makerequest(app, environ=environ)
      connections.register(app)

      request = app.REQUEST
      request['HTTP_ACCEPT_CHARSET'] = 'utf-8'
      connections.register(ERP5TypeTestCaseRequestConnection(request))
      return app

    def __onConnect(self, connector):
      self.__connector_set.add(connector)

    def setUp(self):
      '''Sets up the fixture. Do not override,
         use the hooks instead.
      '''
      from Products.CMFActivity.ActivityRuntimeEnvironment import BaseMessage
      self.__connector_set = set()
      onConnect = self.__onConnect
      self.__original_ZMySQLDA_connect = original_ZMySQLDA_connect = ZMySQLDA_Connection.connect
      def connect(self, *args, **kw):
        onConnect(self)
        return original_ZMySQLDA_connect(self, *args, **kw)
      ZMySQLDA_Connection.connect = connect
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
        app = self._app()
        try:
          template_list[:0] = app._getOb(
            self.getPortalName(),
          ).getCoreBusinessTemplateList()
        finally:
          self.abort()
          ZopeTestCase.close(app)
          del app

      # keep a mapping type info name -> property sheet list, to remove them in
      # tear down.
      self._added_property_sheets = {}
      light_install = self.enableLightInstall()
      create_activities = self.enableActivityTool()
      hot_reindexing = self.enableHotReindexing()
      self._setUpManagerPassword()
      self.setUpERP5Site(business_template_list=template_list,
                         light_install=light_install,
                         create_activities=create_activities,
                         quiet=install_bt5_quiet,
                         hot_reindexing=hot_reindexing,
                         erp5_catalog_storage=erp5_catalog_storage)
      PortalTestCase.setUp(self)
      if os.environ.get('erp5_debug_mode'):
        try:
          self.portal.portal_activities.manage_enableActivityTracking()
          self.commit()
        except AttributeError:
          pass

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

    def loadPromise(self, searchable_business_template_list=None):
      """ Create promise configuration file and load it into configuration

      """
      bt5_repository_path_list = self._getBusinessRepositoryPathList(
                                        searchable_business_template_list)

      promise_path = os.path.join(instancehome, "promise.cfg")
      ZopeTestCase._print('Adding Promise at %s...\n' % promise_path)
      _createTestPromiseConfigurationFile(promise_path, bt5_repository_path_list)
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
      """Update conversion server (Cloudooo) at default site preferences.
      """
      url_list = _getConversionServerUrlList()
      pref = self.getDefaultSystemPreference()
      pref._setPreferredDocumentConversionServerUrlList(url_list)
     # set default retry count in test for network issue
      retry_count = _getConversionServerRetryCount()
      pref._setPreferredDocumentConversionServerRetry(retry_count)

    def _updateMemcachedConfiguration(self):
      """Update default memcached plugin configuration
      """
      portal_memcached = self.portal.portal_memcached
      connection_dict = _getVolatileMemcachedServerDict()
      url_string = '%(hostname)s:%(port)s' % connection_dict
      if portal_memcached.default_memcached_plugin.getUrlString() != url_string:
        portal_memcached.default_memcached_plugin.setUrlString(url_string)

    def _clearActivity(self, quiet=0):
      """Clear activities if `erp5_tests_recreate_catalog` environment variable is
      set. """
      if int(os.environ.get('erp5_tests_recreate_catalog', 0)):
        _start = time.time()
        if not quiet:
          ZopeTestCase._print('\nRecreating activity tables ... ')
        portal = self.getPortal()
        portal.portal_activities.manageClearActivities()
        self.commit()
        if not quiet:
          ZopeTestCase._print('done (%.3fs)\n' % (time.time() - _start,))

    def _recreateCatalog(self, quiet=0):
      """Recreate catalog if `erp5_tests_recreate_catalog` environment variable is
      set. """
      if int(os.environ.get('erp5_tests_recreate_catalog', 0)):
        _start = time.time()
        if not quiet:
          ZopeTestCase._print('\nRecreating catalog ... ')
        portal = self.getPortal()
        portal.portal_catalog.manage_catalogClear()
        self.commit()
        if not quiet:
          ZopeTestCase._print('done (%.3fs)\n' % (time.time() - _start,))

    def _updateTranslationTable(self, quiet=0):
      _start = time.time()
      if not quiet:
        ZopeTestCase._print('\nUpdating translation table ... ')
        self.portal.ERP5Site_updateTranslationTable()
        self.commit()
        if not quiet:
          ZopeTestCase._print('done (%.3fs)\n' % (time.time() - _start,))

    def _reindexSite(self, quiet=0):
      """Reindex site if `erp5_tests_recreate_catalog` environment variable is
      set. """
      if int(os.environ.get('erp5_tests_recreate_catalog', 0)):
        try:
          _start = time.time()
          if not quiet:
            ZopeTestCase._print('\nReindexing site ... ')
          portal = self.getPortal()
          portal.ERP5Site_reindexAll()
          if not quiet:
            ZopeTestCase._print('done (%.3fs)\n' % (time.time() - _start,))
        finally:
          os.environ['erp5_tests_recreate_catalog'] = '0'

    def _installBusinessTemplateList(self, business_template_list,
                                     light_install=True,
                                     quiet=True):
      template_tool = self.portal.portal_templates
      update_business_templates = os.environ.get('update_business_templates') is not None
      erp5_load_data_fs = int(os.environ.get('erp5_load_data_fs', 0))
      BusinessTemplate_getModifiedObject = aq_base(
        getattr(self.portal, 'BusinessTemplate_getModifiedObject', None))

      update_only = os.environ.get('update_only', ())
      if update_only:
        update_only = update_only.split(',')

      def _isUpdateOnlyBusinessTemplate(bt_title):
        for expression in update_only:
          if re.search(expression, bt_title):
            return True

        return False

      update_translation_table = False
      for url, bt_title in business_template_list:
        if (update_business_templates and
            erp5_load_data_fs and
            update_only and
            not _isUpdateOnlyBusinessTemplate(bt_title)):
          continue

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
          listbox_object_list = BusinessTemplate_getModifiedObject.__of__(bt)(
            check_dependencies=False)
          for listbox_line in listbox_object_list:
            install_kw[listbox_line.object_id] = listbox_line.choice_item_list[0][1]
        bt.install(light_install=light_install,
                   object_to_update=install_kw,
                   check_dependencies=False)
        update_translation_table = True
        if bt.isCatalogUpdatable() and (
            int(os.environ.get('erp5_tests_recreate_catalog', 0)) or \
            int(os.environ.get('erp5_load_data_fs', 0)) == 0):
          self.portal.portal_catalog.manage_catalogClear()
        # Release locks
        self.commit()
        if not quiet:
          ZopeTestCase._print('done (%.3fs)\n' % (time.time() - start))
      if update_translation_table:
        self._updateTranslationTable()

    def _getSiteCreationParameterDict(self):
      kw = _getConnectionStringDict()
      # manage_addERP5Site does not accept the following 2 arguments
      for k in ('erp5_sql_deferred_connection_string',
                'erp5_sql_transactionless_connection_string'):
        kw.pop(k, None)
      email_from_address = os.environ.get('email_from_address')
      if email_from_address is not None:
        kw['email_from_address'] = email_from_address
      kw['sql_reset'] = 1
      return kw

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
            # Add user at the root and log in
            uf = app.acl_users
            root_username = 'ERP5TypeTestCase.root'
            self._addUserWithAllRoles(
              user_folder=uf,
              username=root_username,
              password=self.manager_password,
            )
            user = uf.getUserById(root_username).__of__(uf)
            newSecurityManager(None, user)

            # bt5s contain ZODB Components which can be only installed if the
            # user has Developer Role
            addUserToDeveloperRole(root_username)

            # Add ERP5 Site
            reindex = 1
            if hot_reindexing:
              setattr(app, 'isIndexable', 0)
              reindex = 0

            if app._getOb(portal_name, None) is None:
              if not quiet:
                ZopeTestCase._print('Adding %s ERP5 Site ... ' % portal_name)

              kw = self._getSiteCreationParameterDict()
              factory = app.manage_addProduct['ERP5']
              factory.manage_addERP5Site(portal_name,
                                       erp5_catalog_storage=erp5_catalog_storage,
                                       light_install=light_install,
                                       reindex=reindex,
                                       create_activities=create_activities,
                                       **kw)
              sql = kw.get('erp5_sql_connection_string')
              if sql:
                app[portal_name]._setProperty('erp5_site_global_id',
                                              base64.standard_b64encode(str2bytes(sql)))
              if not quiet:
                ZopeTestCase._print('done (%.3fs)\n' % (time.time() - _start))
              # Release locks
              self.commit()
            self.portal = portal = self.getPortal()

            if len(setup_done) == 1: # make sure it is run only once
              self._setUpDummyMailHost()
              self.startHTTPServer(verbose=True)
              self._registerNode(distributing=1, processing=1)
              self.loadPromise()

            self._updateConnectionStrings()
            self._clearActivity()
            self._installBusinessTemplateList(business_template_list,
                                              light_install=light_install,
                                              quiet=quiet)
            self._recreateCatalog()
            self._updateConversionServerConfiguration()
            self._updateMemcachedConfiguration()
            # Create a Manager user at the Portal level.
            self.setUpManagerUser(quiet=quiet)
            uf = self.portal.acl_users
            user = uf.getUserById(self.manager_username).__of__(uf)
            newSecurityManager(None, user)
            addUserToDeveloperRole(self.manager_username)

            self._callSetUpOnce()
            self._reindexSite()

            # Enable reindexing
            # Do hot reindexing # Does not work
            if hot_reindexing:
              setattr(app,'isIndexable', 1)
              portal.portal_catalog.manage_hotReindexAll()

            portal.portal_types.resetDynamicDocumentsOnceAtTransactionBoundary()
            self.tic(not quiet)

            # Log out
            if not quiet:
              ZopeTestCase._print('Logout ...\n')
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
      self.doCleanups()
      if not int(os.environ.get('erp5_save_data_fs', 0)):
        # Drop remaining activities if some of them failed.
        # However, we should not do more activity cleaning, because properly
        # written unit tests should not leave unprocessed activity messages.
        # And the user may want to analyse the result of a failed unit test,
        # so we do nothing in persistent mode (--save).
        try:
          portal_activities = self.portal.portal_activities
          message_list = portal_activities.getMessageList()
        except Exception: # AttributeError, TransactionFailedError ...
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
      if self.__original_ZMySQLDA_connect is not None:
        ZMySQLDA_Connection.connect = self.__original_ZMySQLDA_connect
        for connector in self.__connector_set:
          connector.__dict__.pop('_v_database_connection', None)
        database_connection_pool = Products.ZMySQLDA.DA.database_connection_pool
        for value in six.itervalues(database_connection_pool):
          value.clear()
        database_connection_pool.clear()

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
    # Use an independent request, because this is what happens when using
    # deferred style
    request_form = self.portal.REQUEST.form
    try:
      # XXX maybe there is better API than just replacing the dict
      self.portal.REQUEST.form = dict()
      report_section.pushReport(self.portal)
      form = getattr(here, report_section.getFormId())
      self.portal.REQUEST['here'] = here
      if form.has_field('listbox'):
        result = form.listbox.get_value('default',
                                        render_format='list',
                                        REQUEST=self.portal.REQUEST)
      return result
    finally:
      report_section.popReport(self.portal)
      self.portal.REQUEST.form = request_form

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
  """TestCase class to run a ZEO storage"""

  def setUp(self):
    # Start ZEO storage and send address to parent process if any.
    from Zope2.custom_zodb import zeo_client, Storage
    from ZEO.StorageServer import StorageServer
    storage = {'1': Storage}
    for host_port in parseListeningAddress(os.environ.get('zeo_server')):
      try:
        self.zeo_server = StorageServer(host_port, storage)
        break
      except socket.error as e:
        if e[0] != errno.EADDRINUSE:
          raise
    if zeo_client:
      os.write(zeo_client, repr(host_port))
      os.close(zeo_client)
    ZopeTestCase._print("\nZEO Storage started at %s:%s ... " % host_port)

  def asyncore_loop(self):
    try:
      self.zeo_server.loop()
    except AttributeError: # BBB
      super(ZEOServerTestCase, self).asyncore_loop()
    except KeyboardInterrupt:
      pass

  def tearDown(self):
    self.zeo_server.close()


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
      self.compile(instance)
    return instance.__dict__[self.name]
  def __set__(self, instance, value):
    instance.__dict__[self.name] = value
  def __delete__(self, instance):
    del instance.__dict__[self.name]
  @classmethod
  def compile(cls, instance, _compile=PythonScript._compile):
    instance.__dict__.update(cls.default_dict)
    _compile(instance)

immediate_compilation = 0

@contextmanager
def immediateCompilation():
  global immediate_compilation
  immediate_compilation += 1
  try:
    yield
  finally:
    immediate_compilation -= 1

@onsetup
def optimize():
  '''Significantly reduces portal creation time.'''
  def __init__(self, text):
    # Don't compile expressions on creation
    self.text = text
  from Products.CMFCore.Expression import Expression
  Expression.__init__ = __init__

  # Delay the compilations of Python Scripts until they are really executed.
  # Python Scripts are exported without those 2 attributes:
  PythonScript.func_code = lazy_func_prop('func_code', None)
  PythonScript.__code__ = lazy_func_prop('__code__', None)
  PythonScript.func_defaults = lazy_func_prop('func_defaults', None)
  PythonScript.__defaults__ = lazy_func_prop('__defaults__', None)

  def _compile(self):
    if immediate_compilation:
      return lazy_func_prop.compile(self)
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
    lazy_func_prop.compile(self)
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
    RoleInformation.isIndexable = \
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
    self.__original_init__(value, *args, **kw)
  CacheEntry.__init__ = __init__

  # randomize priorities of activities in a deterministic way
  seed = os.environ.get("random_activity_priority")
  if seed is not None:
    ZopeTestCase._print("RNG seed for priorities of activities is %r\n" % seed)
    rng = random.Random(seed)
    from Products.CMFActivity.ActivityTool import Message
    Message__init__ = Message.__init__
    def __init__(self, url, document_uid, active_process, active_process_uid,
                 activity_kw, *args, **kw):
      activity_kw['priority'] = rng.randint(-128, 127)
      Message__init__(self, url, document_uid, active_process, active_process_uid,
                      activity_kw, *args, **kw)
    Message.__init__ = __init__


fortify()
