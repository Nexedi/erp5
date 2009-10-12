# -*- coding: utf-8 -*-
# Derived from PloneTestCase in Plone.

#
# ERP5TypeTestCase
#

__version__ = '0.3.0'

# XXX make sure that get_request works.
current_app = None
import Products.ERP5Type.Utils
from Products.ERP5Type import Globals

# store a copy of the original method
original_get_request = Globals.get_request

def get_request():
  if current_app is not None:
    return current_app.REQUEST
  else:
    return None

Products.ERP5Type.Utils.get_request = get_request
Globals.get_request = get_request

try:
  import itools.zope
  def get_context():
    return current_app
  itools.zope.get_context = get_context
except ImportError:
  pass

import transaction
from Testing import ZopeTestCase
from Testing.ZopeTestCase.PortalTestCase import PortalTestCase, user_name
from Products.CMFCore.utils import getToolByName
from Products.DCWorkflow.DCWorkflow import ValidationFailed
from Products.ERP5Type.Base import _aq_reset
from zLOG import LOG, DEBUG

# Quiet messages when installing products
install_product_quiet = 1
# Quiet messages when installing business templates
install_bt5_quiet = 0

import OFS.Application
OFS.Application.import_products()

# Std Zope Products
ZopeTestCase.installProduct('ExtFile', quiet=install_product_quiet)
ZopeTestCase.installProduct('Photo', quiet=install_product_quiet)
ZopeTestCase.installProduct('Formulator', quiet=install_product_quiet)
ZopeTestCase.installProduct('FCKeditor', quiet=install_product_quiet)
ZopeTestCase.installProduct('ZSQLMethods', quiet=install_product_quiet)
ZopeTestCase.installProduct('ZMySQLDA', quiet=install_product_quiet)
ZopeTestCase.installProduct('ZSQLCatalog', quiet=install_product_quiet)
ZopeTestCase.installProduct('ZMailIn', quiet=install_product_quiet)
ZopeTestCase.installProduct('ZGDChart', quiet=install_product_quiet)
ZopeTestCase.installProduct('ZCTextIndex', quiet=install_product_quiet)
ZopeTestCase.installProduct('MailHost', quiet=install_product_quiet)
ZopeTestCase.installProduct('PageTemplates', quiet=install_product_quiet)
ZopeTestCase.installProduct('PythonScripts', quiet=install_product_quiet)
ZopeTestCase.installProduct('ExternalMethod', quiet=install_product_quiet)
try:
  # Workaround iHotFix patch that doesn't work with
  # ZopeTestCase REQUESTs
  ZopeTestCase.installProduct('iHotfix', quiet=install_product_quiet)
  from Products import iHotfix
  from types import UnicodeType
  # revert monkey patchs from iHotfix
  iHotfix.get_request = get_request

  originalStringIO = iHotfix.originalStringIO
  class UnicodeSafeStringIO(originalStringIO):
    """StringIO like class which never fails with unicode."""
    def write(self, s):
      if isinstance(s, UnicodeType):
        s = s.encode('utf8', 'repr')
      originalStringIO.write(self, s)
  # iHotFix will patch PageTemplate StringIO with
  iHotfix.iHotfixStringIO = UnicodeSafeStringIO
except ImportError:
  pass
ZopeTestCase.installProduct('Localizer', quiet=install_product_quiet)
try:
  # Workaround Localizer >= 1.2 patch that doesn't work with
  # ZopeTestCase REQUESTs (it's the same as iHotFix
  from Products.Localizer import patches
  from types import UnicodeType
  # revert monkey patchs from Localizer
  patches.get_request = get_request

  class UnicodeSafeStringIO(patches.originalStringIO):
    """StringIO like class which never fails with unicode."""
    def write(self, s):
      if isinstance(s, UnicodeType):
        s = s.encode('utf8', 'repr')
      patches.originalStringIO.write(self, s)
  # Localizer will patch PageTemplate StringIO with
  patches.LocalizerStringIO = UnicodeSafeStringIO
except ImportError:
  pass

ZopeTestCase.installProduct('TimerService', quiet=install_product_quiet)

# CMF
ZopeTestCase.installProduct('CMFCore', quiet=install_product_quiet)
ZopeTestCase.installProduct('CMFDefault', quiet=install_product_quiet)
ZopeTestCase.installProduct('CMFTopic', quiet=install_product_quiet)
ZopeTestCase.installProduct('DCWorkflow', quiet=install_product_quiet)
ZopeTestCase.installProduct('CMFCalendar', quiet=install_product_quiet)

# Based on CMF
ZopeTestCase.installProduct('CMFPhoto', quiet=install_product_quiet)
ZopeTestCase.installProduct('BTreeFolder2', quiet=install_product_quiet)
ZopeTestCase.installProduct('CMFReportTool', quiet=install_product_quiet) # Not required by ERP5Type but required by ERP5Form
ZopeTestCase.installProduct('TranslationService', quiet=install_product_quiet)
ZopeTestCase.installProduct('PortalTransforms', quiet=install_product_quiet)
ZopeTestCase.installProduct('MimetypesRegistry', quiet=install_product_quiet)

# Security Stuff
ZopeTestCase.installProduct('NuxUserGroups', quiet=install_product_quiet)
ZopeTestCase.installProduct('PluggableAuthService', quiet=install_product_quiet)
ZopeTestCase.installProduct('ERP5Security', quiet=install_product_quiet)

# Debugging
ZopeTestCase.installProduct('VerboseSecurity', quiet=install_product_quiet)
ZopeTestCase.installProduct('Zelenium', quiet=install_product_quiet)

# ERP5 - ERP5Type product is installed last so that
#        initializeProductDocumentRegistry is only called
#        after all products which need to register their Document 
#        classes can register them by invoking updateGlobals in __init__
ZopeTestCase.installProduct('CMFActivity', quiet=install_product_quiet)
ZopeTestCase.installProduct('ERP5Catalog', quiet=install_product_quiet)
ZopeTestCase.installProduct('ERP5Form', quiet=install_product_quiet)
ZopeTestCase.installProduct('ERP5', quiet=install_product_quiet)
ZopeTestCase.installProduct('ERP5SyncML', quiet=install_product_quiet)
ZopeTestCase.installProduct('ERP5Type', quiet=install_product_quiet)
ZopeTestCase.installProduct('CMFCategory', quiet=install_product_quiet)
ZopeTestCase.installProduct('ZMySQLDDA', quiet=install_product_quiet)

ZopeTestCase.installProduct('ParsedXML', quiet=install_product_quiet)

# Install everything else which looks like related to ERP5
from OFS.Application import get_products
from App.config import getConfiguration
import os

instancehome = getConfiguration().instancehome
for priority, product_name, index, product_dir in get_products():
  # XXX very heuristic
  if os.path.isdir(os.path.join(product_dir, product_name, 'Document')) \
     or os.path.isdir(os.path.join(product_dir, product_name, 'PropertySheet')) \
     or os.path.isdir(os.path.join(product_dir, product_name, 'Constraint')) \
     or os.path.isdir(os.path.join(product_dir, product_name, 'Tool')):
    ZopeTestCase.installProduct(product_name, quiet=install_product_quiet)

from AccessControl.SecurityManagement import newSecurityManager, noSecurityManager

from Acquisition import aq_base
import time
import md5
import traceback
import os
from cStringIO import StringIO
from urllib import urlretrieve
from glob import glob
import sys, re, base64

portal_name = 'erp5_portal'

# we keep a reference to all sites for wich setup failed the first time, to
# prevent replaying the same failing setup step for each test.
failed_portal_installation = {}

# have we installed business templates ?
# this is a mapping 'list of business template -> boolean
setup_done = {}


def _getConnectionStringDict():
  """Returns the connection strings used for this test.
  """
  connection_string_dict = {}
  erp5_sql_connection_string = os.environ.get(
                                    'erp5_sql_connection_string')
  if erp5_sql_connection_string:
    connection_string_dict['erp5_sql_connection_string'] = \
                                erp5_sql_connection_string
  cmf_activity_sql_connection_string = os.environ.get(
                            'cmf_activity_sql_connection_string',
                            os.environ.get('erp5_sql_connection_string'))
  if cmf_activity_sql_connection_string:
    connection_string_dict['cmf_activity_sql_connection_string'] = \
                                cmf_activity_sql_connection_string
    erp5_sql_transactionless_connection_string = os.environ.get(
             'erp5_sql_transactionless_connection_string',
             '-%s' % cmf_activity_sql_connection_string)
    if erp5_sql_transactionless_connection_string:
      connection_string_dict['erp5_sql_transactionless_connection_string'] = \
                              erp5_sql_transactionless_connection_string
  return connection_string_dict


class ERP5TypeTestCase(PortalTestCase):
    """TestCase for ERP5 based tests.

    This TestCase setups an ERP5Site and installs business templates.
    """

    def shortDescription(self):
        doc = self._TestCase__testMethodDoc
        return doc and str(self) + ', ' + doc.split("\n")[0].strip() or None

    def dummy_test(self):
      ZopeTestCase._print('All tests are skipped when --save option is passed '
                          'with --update_business_templates or without --load')

    def getRevision(self):
      try:
        import pysvn
        return pysvn.Client().info('%s/Products/ERP5'
                    % os.environ['INSTANCE_HOME']).revision.number
      except:
        return None

    def getTitle(self):
      """Returns the title of the test, for test reports.
      """
      return str(self.__class__)

    def getPortalName(self):
      """
        Return the name of a portal for this test case.
        This is necessary for each test case to use a different portal built by
        different business templates.
        The test runner can set `erp5_tests_portal_id` environnement variable
        to force a portal id.
      """
      forced_portal_id = os.environ.get('erp5_tests_portal_id')
      if forced_portal_id:
        return str(forced_portal_id)
      m = md5.new()
      m.update(repr(self.getBusinessTemplateList())+ self.getTitle())
      uid = m.hexdigest()

      return portal_name + '_' + uid

    def getPortal(self):
      """Returns the portal object, i.e. the "fixture root".
      """
      return self.app[self.getPortalName()]

    getPortalObject = getPortal

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

    def login(self, quiet=0):
      """
      Most of the time, we need to login before doing anything
      """
      uf = self.getPortal().acl_users
      uf._doAddUser('ERP5TypeTestCase', '', ['Manager', 'Member', 'Assignee',
          'Assignor', 'Author', 'Auditor', 'Associate'], [])
      user = uf.getUserById('ERP5TypeTestCase').__of__(uf)
      newSecurityManager(None, user)

    def _setupUser(self):
      '''Creates the default user.'''
      uf = self.portal.acl_users
      # do nothing if the user already exists
      if not uf.getUser(user_name):
        uf._doAddUser(user_name, 'secret', ['Member'], [])

    def setUp(self):
      '''Sets up the fixture. Do not override,
         use the hooks instead.
      '''
      # This is a workaround for the overwriting problem in Testing/__init__.py
      # in Zope.  So this overwrites them again to revert the changes made by
      # Testing.
      try:
        import App.config
      except ImportError:
        os.environ['INSTANCE_HOME'] = INSTANCE_HOME =\
                            os.environ['COPY_OF_INSTANCE_HOME']
        os.environ['SOFTWARE_HOME'] = SOFTWARE_HOME =\
                            os.environ['COPY_OF_SOFTWARE_HOME']
      else:
        cfg = App.config.getConfiguration()
        cfg.instancehome = os.environ['COPY_OF_INSTANCE_HOME']
        App.config.setConfiguration(cfg)
      INSTANCE_HOME = os.environ['INSTANCE_HOME']
      bt5_path = os.environ.get('erp5_tests_bt5_path',
                            os.path.join(INSTANCE_HOME, 'bt5'))
      bootstrap_path = os.environ.get('erp5_tests_bootstrap_path',
                                  os.path.join(INSTANCE_HOME, 'Products/ERP5/bootstrap'))

      template_list = self.getBusinessTemplateList()
      erp5_catalog_storage = os.environ.get('erp5_catalog_storage',
                                            'erp5_mysql_innodb_catalog')
      update_business_templates = os.environ.get('update_business_templates') is not None
      erp5_load_data_fs = int(os.environ.get('erp5_load_data_fs', 0))
      if update_business_templates and erp5_load_data_fs:
        update_only = os.environ.get('update_only', None)
        template_list = (erp5_catalog_storage, 'erp5_core',
                         'erp5_xhtml_style') + tuple(template_list)
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
      new_template_list = []
      for template in template_list:
        id = template.split('/')[-1]
        try :
          file, headers = urlretrieve(template)
        except IOError :
          # First, try the bt5 directory itself.
          path = os.path.join(bt5_path, template)
          alternate_path = os.path.join(bootstrap_path, template)
          if os.path.exists(path):
            template = path
          elif os.path.exists(alternate_path):
            template = alternate_path
          else:
            path = '%s.bt5' % path
            if os.path.exists(path):
              template = path
            else:
              # Otherwise, look at sub-directories.
              # This is for backward-compatibility.
              path = os.path.join(INSTANCE_HOME, 'bt5', '*', template)
              template_list = glob(path)
              if len(template_list) == 0:
                template_list = glob('%s.bt5' % path)
              if len(template_list) and template_list[0]:
                template = template_list[0]
              else:
                # The last resort is current directory.
                template = '%s' % id
                if not os.path.exists(template):
                  template = '%s.bt5' % id
        else:
          template = '%s' % template
          if not os.path.exists(template):
            template = '%s.bt5' % template
        new_template_list.append((template,id))

      light_install = self.enableLightInstall()
      create_activities = self.enableActivityTool()
      hot_reindexing = self.enableHotReindexing()
      self.setUpERP5Site(business_template_list=new_template_list,
                         light_install=light_install,
                         create_activities=create_activities,
                         quiet=install_bt5_quiet,
                         hot_reindexing=hot_reindexing,
                         erp5_catalog_storage=erp5_catalog_storage)
      PortalTestCase.setUp(self)
      global current_app
      current_app = self.app
      self._updateConnectionStrings()

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

    def logMessage(self, message):
      """
        Shortcut function to log a message
      """
      ZopeTestCase._print('\n%s ' % message)
      LOG('Testing ... ', DEBUG, message)

    def _updateConnectionStrings(self):
      """Update connection strings with values passed by the testRunner
      """
      global current_app
      if current_app is not None:
        self.app = current_app
      portal = self.getPortal()
      # update connection strings
      for connection_string_name, connection_string in\
                                    _getConnectionStringDict().items():
        connection_name = connection_string_name.replace('_string', '')
        getattr(portal, connection_name).edit('', connection_string)

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
          transaction.commit()
          portal.ERP5Site_reindexAll()
          transaction.commit()
          self.tic()
          if not quiet:
            ZopeTestCase._print('done (%.3fs)\n' % (time.time() - _start,))
        finally:
          os.environ['erp5_tests_recreate_catalog'] = '0'

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
                         property_sheet_code=None):
      """Utility method to add a property sheet to a type information.
      You might be interested in the higer level method _addProperty
      This method registers all added property sheets, to be able to remove
      them in tearDown.
      """
      # install the 'real' class tool
      class_tool = self.getClassTool()

      if property_sheet_code is not None:
        class_tool.newPropertySheet(property_sheet_name)
        # XXX need to commit the transaction at this point, because class tool
        # files are no longer available to the current transaction.
        transaction.commit()
        class_tool.editPropertySheet(property_sheet_name, property_sheet_code)
        transaction.commit()
        class_tool.importPropertySheet(property_sheet_name)
      
      # We set the property sheet on the portal type
      ti = self.getTypesTool().getTypeInfo(portal_type_name)
      if property_sheet_name not in ti.property_sheet_list:
        ti.property_sheet_list = list(ti.property_sheet_list) +\
                                    [property_sheet_name]

      # remember that we added a property sheet for tear down
      if getattr(self, '_added_property_sheets', None) is not None:
        self._added_property_sheets.setdefault(
                    portal_type_name, []).append(property_sheet_name)
      # reset aq_dynamic cache
      _aq_reset()

    def validateRules(self):
      """
      try to validate all rules in rule_tool.
      """
      rule_tool = self.getRuleTool()
      for rule in rule_tool.contentValues(
          portal_type=rule_tool.getPortalRuleTypeList()):
        if rule.getValidationState() != 'validated':
          rule.validate()

    def tic(self, verbose=0):
      """
      Start all messages
      """
      portal_activities = getattr(self.getPortal(),'portal_activities',None)
      if portal_activities is not None:
        if verbose:
          ZopeTestCase._print('Executing pending activities ...')
          old_message_count = 0
          start = time.time()
        count = 1000
        message_count = len(portal_activities.getMessageList())
        while message_count:
          if verbose and old_message_count != message_count:
            ZopeTestCase._print(' %i' % message_count)
            old_message_count = message_count
          portal_activities.process_timer(None, None)
          message_count = len(portal_activities.getMessageList())
          # This prevents an infinite loop.
          count -= 1
          if count == 0:
            # Get the last error message from error_log.
            error_message = ''
            error_log = self.getPortal().error_log._getLog()
            if len(error_log):
              last_log = error_log[-1]
              error_message = '\nLast error message:\n%s\n%s\n%s\n' % (
                last_log['type'],
                last_log['value'],
                last_log['tb_text'],
                )
            raise RuntimeError,\
              'tic is looping forever. These messages are pending: %r %s' % (
            [('/'.join(m.object_path), m.method_id, m.processing_node, m.priority)
            for m in portal_activities.getMessageList()],
            error_message
            )
          # This give some time between messages
          if count % 10 == 0:
            from Products.CMFActivity.Activity.Queue import VALIDATION_ERROR_DELAY
            portal_activities.timeShift(3 * VALIDATION_ERROR_DELAY)
        if verbose:
          ZopeTestCase._print(' done (%.3fs)\n' % (time.time() - start))

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
        person_kw = dict()

      person = self.portal.person_module.newContent(portal_type='Person',
                                                    reference=reference,
                                                    password=password,
                                                    **person_kw)
      return person

    def createUserAssignement(self, user, assignment_kw):
      """
        Create an assignment to user.
      """
      assignment = user.newContent(portal_type='Assignment', **assignment_kw)
      assignment.open()
      return assignment

    def failIfDifferentSet(self, a, b, msg=""):
      if not msg:
        msg='%r != %r' % (a, b)
      for i in a:
        self.failUnless(i in b, msg)
      for i in b:
        self.failUnless(i in a, msg)
      self.assertEquals(len(a), len(b), msg)
    assertSameSet = failIfDifferentSet

    def assertWorkflowTransitionFails(self, object, workflow_id, transition_id, error_message=None):
      """
        Check that passing given transition from given workflow on given object
        raises ValidationFailed.
        Do sanity checks (workflow history length increased by one, simulation
        state unchanged).
        If error_message is provided, it is asserted to be equal to the last
        workflow history error message.
      """
      reference_history_length = len(self.workflow_tool.getInfoFor(ob=object, name='history', wf_id=workflow_id))
      reference_workflow_state = object.getSimulationState()
      self.assertRaises(ValidationFailed, self.workflow_tool.doActionFor, object, transition_id, wf_id=workflow_id)
      workflow_history = self.workflow_tool.getInfoFor(ob=object, name='history', wf_id=workflow_id)
      self.assertEqual(len(workflow_history), reference_history_length + 1)
      workflow_error_message = str(workflow_history[-1]['error_message'])
      if error_message is not None:
        self.assertEqual(workflow_error_message, error_message)
      self.assertEqual(object.getSimulationState(), reference_workflow_state)
      return workflow_error_message

    def setUpERP5Site(self,
                     business_template_list=(),
                     app=None,
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
      from Products.ERP5Type.Base import _aq_reset
      if portal_name in failed_portal_installation:
        raise RuntimeError, 'Installation of %s already failed, giving up'\
                              % portal_name
      try:
        if app is None:
          app = ZopeTestCase.app()
        # this app will be closed after setUp, but keep an reference anyway, to
        # make it's REQUEST available during setup
        global current_app
        current_app = app

        global setup_done
        if not (hasattr(aq_base(app), portal_name) and
                 setup_done.get(tuple(business_template_list))):
          setup_done[tuple(business_template_list)] = 1
          try:
            _start = time.time()
            # Add user and log in
            if not quiet:
              ZopeTestCase._print('\nAdding ERP5TypeTestCase user ... \n')
            uf = app.acl_users
            uf._doAddUser('ERP5TypeTestCase', '', ['Manager', 'Member', 'Assignee',
                          'Assignor', 'Author', 'Auditor', 'Associate'], [])
            user = uf.getUserById('ERP5TypeTestCase').__of__(uf)
            newSecurityManager(None, user)
            # Add ERP5 Site
            reindex = 1
            if hot_reindexing:
              setattr(app, 'isIndexable', 0)
              reindex = 0

            portal = getattr(app, portal_name, None)
            if portal is None:
              if not quiet:
                ZopeTestCase._print('Adding %s ERP5 Site ... ' % portal_name)

              extra_constructor_kw = _getConnectionStringDict()
              # manage_addERP5Site does not accept
              # erp5_sql_transactionless_connection_string argument
              extra_constructor_kw.pop(
                    'erp5_sql_transactionless_connection_string', None)
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
              portal = app[portal_name]

              if not quiet:
                ZopeTestCase._print('done (%.3fs)\n' % (time.time() - _start))
              # Release locks
              transaction.commit()
            self.portal = portal

            if len(setup_done) == 1: # make sure it is run only once
              try:
                from Products import DeadlockDebugger
              except ImportError:
                pass
              from Testing.ZopeTestCase.utils import startZServer
              ZopeTestCase._print('Running ZServer on port %i\n'
                                  % startZServer()[1])

            self._updateConnectionStrings()
            self._recreateCatalog()

            update_business_templates = os.environ.get('update_business_templates') is not None
            BusinessTemplate_getModifiedObject = aq_base(getattr(portal, 'BusinessTemplate_getModifiedObject', None))

            # Add some business templates
            for url, bt_title in business_template_list:
              start = time.time()
              get_install_kw = False
              if bt_title in [x.getTitle() for x in portal.portal_templates.getInstalledBusinessTemplateList()]:
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
              bt = portal.portal_templates.download(url)
              if not quiet:
                ZopeTestCase._print('(imported in %.3fs) ' % (time.time() - start))
              install_kw = None
              if get_install_kw:
                install_kw = {}
                listbox_object_list = BusinessTemplate_getModifiedObject.__of__(bt)()
                for listbox_line in listbox_object_list:
                  install_kw[listbox_line.object_id] = listbox_line.choice_item_list[0][1]
              bt.install(light_install=light_install,
                         object_to_update=install_kw,
                         update_translation=1)
              # Release locks
              transaction.commit()
              if not quiet:
                ZopeTestCase._print('done (%.3fs)\n' % (time.time() - start))

            setup_once = getattr(self, 'setUpOnce', None)
            if setup_once is not None and \
                   not getattr(portal, 'set_up_once_called', 0):
              portal.set_up_once_called = 1
              if not quiet:
                ZopeTestCase._print('Executing setUpOnce ... ')
                start = time.time()
              # setUpOnce method may use self.app and self.portal
              self.app = app
              setup_once()
              if not quiet:
                ZopeTestCase._print('done (%.3fs)\n' % (time.time() - start))

            # Enable reindexing
            # Do hot reindexing # Does not work
            if hot_reindexing:
              setattr(app,'isIndexable', 1)
              portal.portal_catalog.manage_hotReindexAll()

            transaction.commit()
            self.tic(not quiet)

            # Reset aq dynamic, so all unit tests will start again
            _aq_reset()

            # Log out
            if not quiet:
              ZopeTestCase._print('Logout ... \n')
            noSecurityManager()
            if not quiet:
              ZopeTestCase._print('done (%.3fs)\n' % (time.time()-_start,))
              ZopeTestCase._print('Ran Unit test of %s\n' % title)
          except:
            transaction.abort()
            raise
          else:
            transaction.commit()
            ZopeTestCase.close(app)
      except:
        f = StringIO()
        traceback.print_exc(file=f)
        ZopeTestCase._print(f.getvalue())
        f.close()
        failed_portal_installation[portal_name] = 1
        ZopeTestCase._print('Ran Unit test of %s (installation failed)\n'
                            % title) # run_unit_test depends on this string.
        raise

    def beforeClose(self):
      PortalTestCase.beforeClose(self)
      try:
        # portal_activities.process_timer automatically registers current node
        # (localhost:<random_port>). We must unregister it so that Data.fs can
        # be reused without reconfiguring portal_activities.
        portal_activities = self.portal.portal_activities
        del portal_activities.distributingNode
        del portal_activities._nodes
        transaction.commit()
      except AttributeError:
        pass

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

        from StringIO import StringIO
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


class ResponseWrapper:
    '''Decorates a response object with additional introspective methods.'''

    _bodyre = re.compile('^$^\n(.*)', re.MULTILINE | re.DOTALL)

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
        body = self._bodyre.search(self.getOutput())
        if body is not None:
            body = body.group(1)
        return body

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
    if hasattr(report, 'report_method'):
      report_method = getattr(context, report.report_method)
      return report_method()
    else:
      report_item_list = []
      for reportbox in [field for field in report.get_fields()
                        if field.getRecursiveTemplateField().meta_type == 'ReportBox']:
        report_item_list.extend(reportbox.render())
      return report_item_list

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

from unittest import _makeLoader, TestSuite

def dummy_makeSuite(testCaseClass, prefix='dummy_test', sortUsing=cmp, suiteClass=TestSuite):
  return _makeLoader(prefix, sortUsing, suiteClass).loadTestsFromTestCase(testCaseClass)

def dummy_setUp(self):
  '''
  This one is overloaded so that it dos not execute beforeSetUp and afterSetUp
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
  This one is overloaded so that it dos not execute beforeTearDown from
  the original tests, which would write to the FileStorage when --save
  is enabled
  '''
  self._clear(1)

def optimize():
  '''Significantly reduces portal creation time.'''
  def __init__(self, text):
    # Don't compile expressions on creation
    self.text = text
  from Products.CMFCore.Expression import Expression
  Expression.__init__ = __init__

  # Delay the compilations of Python Scripts until they are really executed.
  from Products.PythonScripts.PythonScript import PythonScript
  PythonScript_compile = PythonScript._compile
  def _compile(self):
    self._lazy_compilation = 1
  PythonScript._compile = _compile
  PythonScript_exec = PythonScript._exec
  def _exec(self, *args):
    if getattr(self, '_lazy_compilation', 0):
      self._lazy_compilation = 0
      PythonScript_compile(self)
    return PythonScript_exec(self, *args)
  PythonScript._exec = _exec
  from Acquisition import aq_parent
  def _makeFunction(self, dummy=0): # CMFCore.FSPythonScript uses dummy arg.
    self.ZCacheable_invalidate()
    PythonScript_compile(self)
    if not (aq_parent(self) is None or hasattr(self, '_filepath')):
      # It needs a _filepath, and has an acquisition wrapper.
      self._filepath = self.get_filepath()
  PythonScript._makeFunction = _makeFunction

optimize()


def fortify():
  '''Add some extra checks that we don't have at runtime, not to slow down the
  system.
  '''
  # check that we don't store persistent objects in cache
  from pickle import dumps
  from Products.ERP5Type.CachePlugins.BaseCache import CacheEntry
  CacheEntry__init__ = CacheEntry.__init__
  def __init__(self, value, *args, **kw):
    # this will raise TypeError if you try to cache a persistent object
    dumps(value)
    CacheEntry__init__(self, value, *args, **kw)
  CacheEntry.__init__ = __init__

fortify()
