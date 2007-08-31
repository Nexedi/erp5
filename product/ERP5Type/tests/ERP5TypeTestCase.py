# Derived from PloneTestCase in Plone.

#
# ERP5TypeTestCase
#

__version__ = '0.3.0'

# XXX: Suppress DeprecationWarnings
import warnings
warnings.simplefilter('ignore', DeprecationWarning, append=1)

# XXX make sure that get_request works.
current_app = None
import Products.ERP5Type.Utils
import Globals

# store a copy of the original method
original_get_request = Globals.get_request

def get_request():
  if current_app is not None:
    return current_app.REQUEST
  else:
    return None

Products.ERP5Type.Utils.get_request = get_request
Globals.get_request = get_request

import itools.zope

def get_context():
  return current_app

itools.zope.get_context = get_context

from Testing import ZopeTestCase
from Testing.ZopeTestCase.PortalTestCase import PortalTestCase, user_name
from Products.ERP5Type.tests.utils import getMySQLArguments
from Products.CMFCore.utils import getToolByName
from Products.ERP5Type.Utils import getLocalPropertySheetList, \
                                    removeLocalPropertySheet, \
                                    importLocalPropertySheet
from Products.ERP5Type.Utils import getLocalDocumentList, \
                                    removeLocalDocument, \
                                    importLocalDocument
from Products.ERP5Type.Utils import getLocalConstraintList, \
                                    removeLocalConstraint, \
                                    importLocalConstraint
from Products.DCWorkflow.DCWorkflow import ValidationFailed
from zLOG import LOG, DEBUG

try:
  from transaction import get as get_transaction
except ImportError:
  pass

# Quiet messages when installing products
install_product_quiet = 1
# Quiet messages when installing business templates
install_bt5_quiet = 0

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
  from StringIO import StringIO as OrigStringIO
  from types import UnicodeType
  # revert monkey patchs from iHotfix
  iHotfix.get_request = get_request

  class UnicodeSafeStringIO(OrigStringIO):
    """StringIO like class which never fails with unicode."""
    def write(self, s):
      if isinstance(s, UnicodeType):
        s = s.encode('utf8', 'repr')
      OrigStringIO.write(self, s)
  # iHotFix will patch PageTemplate StringIO with
  iHotfix.iHotfixStringIO = UnicodeSafeStringIO
except ImportError:
  pass
ZopeTestCase.installProduct('Localizer', quiet=install_product_quiet)
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
ZopeTestCase.installProduct('CMFMailIn', quiet=install_product_quiet)
ZopeTestCase.installProduct('TranslationService', quiet=install_product_quiet)

# Security Stuff
ZopeTestCase.installProduct('NuxUserGroups', quiet=install_product_quiet)
ZopeTestCase.installProduct('PluggableAuthService', quiet=install_product_quiet)
ZopeTestCase.installProduct('ERP5Security', quiet=install_product_quiet)

# Debugging
ZopeTestCase.installProduct('VerboseSecurity', quiet=install_product_quiet)
ZopeTestCase.installProduct('Zelenium', quiet=install_product_quiet)

# ERP5
ZopeTestCase.installProduct('CMFActivity', quiet=install_product_quiet)
ZopeTestCase.installProduct('ERP5Catalog', quiet=install_product_quiet)
ZopeTestCase.installProduct('ERP5Type', quiet=install_product_quiet)
ZopeTestCase.installProduct('ERP5Form', quiet=install_product_quiet)
ZopeTestCase.installProduct('ERP5SyncML', quiet=install_product_quiet)
ZopeTestCase.installProduct('CMFCategory', quiet=install_product_quiet)
ZopeTestCase.installProduct('ERP5', quiet=install_product_quiet)
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

# Install Document types (circumvent different init order in ZopeTestCase)
from Products.ERP5Type.InitGenerator import initializeProductDocumentRegistry
initializeProductDocumentRegistry()

from AccessControl.SecurityManagement import newSecurityManager, noSecurityManager

from Acquisition import aq_base
import time
import md5
import traceback
import os
from cStringIO import StringIO
from urllib import urlretrieve
from glob import glob
import pysvn

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
  erp5_sql_deferred_connection_string = os.environ.get(
                            'erp5_sql_deferred_connection_string',
                            os.environ.get('erp5_sql_connection_string'))
  if erp5_sql_deferred_connection_string:
    connection_string_dict['erp5_sql_deferred_connection_string'] = \
                                erp5_sql_deferred_connection_string
  return connection_string_dict


class ERP5TypeTestCase(PortalTestCase):
    """TestCase for ERP5 based tests.

    This TestCase setups an ERP5Site and installs business templates.
    """

    def dummy_test(self):
      ZopeTestCase._print('All tests are skipped with --save option.')

    def getRevision(self):
      try:
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

      template_list = self.getBusinessTemplateList()
      new_template_list = []
      #LOG('template_list',0,template_list)
      for template in template_list:
        id = template
        try :
          file, headers = urlretrieve(template)
        except IOError :
          # First, try the bt5 directory itself.
          path = os.path.join(bt5_path, template)
          if os.path.exists(path):
            template = path
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
      erp5_catalog_storage = os.environ.get('erp5_catalog_storage',
                                            'erp5_mysql_innodb_catalog')
      setupERP5Site(business_template_list=new_template_list,
                    light_install=light_install,
                    portal_name=self.getPortalName(),
                    title=self.getTitle(),
                    create_activities=create_activities,
                    quiet=install_bt5_quiet,
                    hot_reindexing=hot_reindexing,
                    erp5_catalog_storage=erp5_catalog_storage)
      PortalTestCase.setUp(self)
      global current_app
      current_app = self.app
      self._updateConnectionStrings()
      self._recreateCatalog()

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
      portal = self.getPortal()
      if int(os.environ.get('erp5_tests_recreate_catalog', 0)):
        try:
          self.login()
          _start = time.time()
          if not quiet:
            ZopeTestCase._print('\nRecreating catalog ... ')
          portal.portal_activities.manageClearActivities()
          portal.portal_catalog.manage_catalogClear()
          get_transaction().commit()
          portal.ERP5Site_reindexAll()
          get_transaction().commit()
          self.tic()
          if not quiet:
            ZopeTestCase._print('done (%.3fs)\n' % (time.time() - _start,))
        finally:
          os.environ['erp5_tests_recreate_catalog'] = '0'
          noSecurityManager()

    # Utility methods specific to ERP5Type
    def getTemplateTool(self):
      return getToolByName(self.getPortal(), 'portal_templates', None)

    def getPreferenceTool(self) :
      return getToolByName(self.getPortal(), 'portal_preferences', None)

    def getTrashTool(self):
      return getToolByName(self.getPortal(), 'portal_trash', None)

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

    def getOrganisationModule(self):
      return getattr(self.getPortal(), 'organisation_module',
          getattr(self.getPortal(), 'organisation', None))

    def getPersonModule(self):
      return getattr(self.getPortal(), 'person_module',
          getattr(self.getPortal(), 'person', None))

    def getCurrencyModule(self):
      return getattr(self.getPortal(), 'currency_module',
          getattr(self.getPortal(), 'currency', None))

    def tic(self):
      """
      Start all messages
      """
      portal_activities = getattr(self.getPortal(),'portal_activities',None)
      if portal_activities is not None:
        count = 1000
        while len(portal_activities.getMessageList()) > 0:
          portal_activities.process_timer(None, None)
          # This prevents an infinite loop.
          count -= 1
          if count == 0:
            raise RuntimeError,\
              'tic is looping forever. These messages are pending: %r' % (
            [('/'.join(m.object_path), m.method_id, m.processing_node, m.priority)
            for m in portal_activities.getMessageList()],)
          # This give some time between messages
          if count % 10 == 0:
            from Products.CMFActivity.Activity.Queue import VALIDATION_ERROR_DELAY
            portal_activities.timeShift(3 * VALIDATION_ERROR_DELAY)

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

def setupERP5Site( business_template_list=(),
                   app=None,
                   portal_name=portal_name,
                   title='',
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
            get_transaction().commit()

          if os.environ.get('erp5_load_data_fs'):
            # Import local PropertySheets, Documents
            for id_ in getLocalPropertySheetList():
              importLocalPropertySheet(id_)
            for id_ in getLocalDocumentList():
              importLocalDocument(id_)
            for id_ in getLocalConstraintList():
              importLocalConstraint(id_)
          else:
            # Remove all local PropertySheets, Documents
            for id_ in getLocalPropertySheetList():
              removeLocalPropertySheet(id_)
            for id_ in getLocalDocumentList():
              removeLocalDocument(id_)
            for id_ in getLocalConstraintList():
              removeLocalConstraint(id_)

          # Disable reindexing before adding templates
          # VERY IMPORTANT: Add some business templates
          for url, id_ in business_template_list:
            start = time.time()
            if id_ in portal.portal_templates.objectIds():
              continue
            if not quiet:
              ZopeTestCase._print('Adding %s business template ... ' % id_)
            portal.portal_templates.download(url, id=id_)
            portal.portal_templates[id_].install(light_install=light_install)
            # Release locks
            get_transaction().commit()
            if not quiet:
              ZopeTestCase._print('done (%.3fs)\n' % (time.time() - start))

          # Enable reindexing
          # Do hot reindexing # Does not work
          if hot_reindexing:
            setattr(app,'isIndexable', 1)
            portal.portal_catalog.manage_hotReindexAll()

          get_transaction().commit()
          portal_activities = getattr(portal, 'portal_activities', None)
          if portal_activities is not None:
            count = 1000
            while len(portal_activities.getMessageList()) > 0:
              portal_activities.distribute()
              portal_activities.tic()
              get_transaction().commit()
              count -= 1
              if count == 0:
                raise RuntimeError, \
                'tic is looping forever. These messages are pending: %r' % (
                    [('/'.join(m.object_path), m.method_id,
                     m.processing_node, m.priority)
                     for m in portal_activities.getMessageList()],)

          # Reset aq dynamic, so all unit tests will start again
          _aq_reset()

          if os.environ.get('erp5_save_data_fs'):
            # Quit the test in order to get a clean site
            if not quiet:
              ZopeTestCase._print('done (%.3fs)\n' % (time.time()-_start,))
            get_transaction().commit()
            ZopeTestCase.close(app)
            if not quiet:
              ZopeTestCase._print('Data.fs created\n')
            get_transaction().commit()
            ZopeTestCase.close(app)
            if not quiet:
              ZopeTestCase._print('Dumping MySQL database ... ')
            instance_home = os.environ['INSTANCE_HOME']
            os.system('mysqldump %s > %s/dump.sql' % (
                      getMySQLArguments(), instance_home))
            if not quiet:
              ZopeTestCase._print('Dumping static files ... ')
            for dir in ('Constraint', 'Document', 'PropertySheet'):
              os.system('rm -rf %s/%s.bak' % (instance_home, dir))
              os.system('cp -ar %s/%s %s/%s.bak' % (instance_home, dir, instance_home, dir))
 
          # Log out
          if not quiet:
            ZopeTestCase._print('Logout ... \n')
          noSecurityManager()
          if not quiet:
            ZopeTestCase._print('done (%.3fs)\n' % (time.time()-_start,))
            ZopeTestCase._print('Ran Unit test of %s\n' % title)
        except:
          get_transaction().abort()
          raise
        else:
          get_transaction().commit()
          ZopeTestCase.close(app)

      if os.environ.get('erp5_load_data_fs'):
        # Import local PropertySheets, Documents
        # when loading an environnement
        for id_ in getLocalPropertySheetList():
          importLocalPropertySheet(id_)
        for id_ in getLocalDocumentList():
          importLocalDocument(id_)
        for id_ in getLocalConstraintList():
          importLocalConstraint(id_)
        _aq_reset()

    except:
      f = StringIO()
      traceback.print_exc(file=f)
      ZopeTestCase._print(f.getvalue())
      f.close()
      failed_portal_installation[portal_name] = 1
      ZopeTestCase._print('Ran Unit test of %s (installation failed)\n'
                          % title) # run_unit_test depends on this string.
      raise

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
      self.app = self._app()
      self.portal = self._portal()
      self._setup()
  except:
      self._clear()
      raise

def dummy_tearDown(self):
  '''
  This one is overloaded so that it dos not execute beforeTearDown and
  afterTearDown from the original tests, which would write to the
  FileStorage when --save is enabled
  '''
  pass

def optimize():
  '''Significantly reduces portal creation time.'''
  def __init__(self, text):
    # Don't compile expressions on creation
    self.text = text
  from Products.CMFCore.Expression import Expression
  Expression.__init__ = __init__

optimize()
