# Derived from PloneTestCase in Plone.

#
# ERP5TypeTestCase
#

__version__ = '0.3.0'

from Testing import ZopeTestCase
from Testing.ZopeTestCase.PortalTestCase import PortalTestCase, user_name
from Products.CMFCore.utils import getToolByName
from Products.ERP5Type.Utils import getLocalPropertySheetList, removeLocalPropertySheet
from Products.ERP5Type.Utils import getLocalDocumentList, removeLocalDocument
from Products.ERP5Type.Utils import getLocalConstraintList, removeLocalConstraint
from zLOG import LOG

try:
  from transaction import get as get_transaction
except ImportError:
  pass

# Std Zope Products
ZopeTestCase.installProduct('ExtFile')
ZopeTestCase.installProduct('Photo')
ZopeTestCase.installProduct('Formulator')
ZopeTestCase.installProduct('ZSQLMethods')
ZopeTestCase.installProduct('ZMySQLDA')
ZopeTestCase.installProduct('ZSQLCatalog')
ZopeTestCase.installProduct('ZMailIn')
ZopeTestCase.installProduct('ZGDChart')
ZopeTestCase.installProduct('ZCTextIndex')
ZopeTestCase.installProduct('MailHost')
ZopeTestCase.installProduct('PageTemplates')
ZopeTestCase.installProduct('PythonScripts')
ZopeTestCase.installProduct('ExternalMethod')
ZopeTestCase.installProduct('Localizer')
ZopeTestCase.installProduct('TimerService')

# CMF
ZopeTestCase.installProduct('CMFCore')
ZopeTestCase.installProduct('CMFDefault')
ZopeTestCase.installProduct('CMFTopic')
ZopeTestCase.installProduct('DCWorkflow')
ZopeTestCase.installProduct('CMFCalendar')

# Based on CMF
ZopeTestCase.installProduct('CMFPhoto')
ZopeTestCase.installProduct('BTreeFolder2')
ZopeTestCase.installProduct('CMFReportTool') # Not required by ERP5Type but required by ERP5Form
ZopeTestCase.installProduct('CMFMailIn')
ZopeTestCase.installProduct('TranslationService')

# Security Stuff
ZopeTestCase.installProduct('NuxUserGroups')
ZopeTestCase.installProduct('PluggableAuthService')
ZopeTestCase.installProduct('ERP5Security')

# Debugging
ZopeTestCase.installProduct('VerboseSecurity')

# ERP5
ZopeTestCase.installProduct('CMFActivity')
ZopeTestCase.installProduct('ERP5Catalog')
ZopeTestCase.installProduct('ERP5Type')
ZopeTestCase.installProduct('ERP5Form') # Not required by ERP5Type but required by ERP5Form
ZopeTestCase.installProduct('ERP5SyncML')
ZopeTestCase.installProduct('CMFCategory')
ZopeTestCase.installProduct('Nexedi')
ZopeTestCase.installProduct('ERP5') # Not needed by ERP5Type

# Coramy
ZopeTestCase.installProduct('Coramy')

# Install Document types (circumvent different init order in ZopeTestCase)
from Products.ERP5Type.InitGenerator import initializeProductDocumentRegistry
initializeProductDocumentRegistry()

from AccessControl.SecurityManagement import newSecurityManager, noSecurityManager
from AccessControl.User import User

from Acquisition import aq_base
import time
import md5
import traceback
import sys
import os
from cStringIO import StringIO

from Products.ERP5.ERP5Site import ERP5Site

portal_name = 'erp5_portal'

class ERP5TypeTestCase(PortalTestCase):

    def getTitle(self):
      """
      """
      return "Default Title of Test"

    def getPortalName(self):
      """
        Return the name of a portal for this test case.
        This is necessary for each test case to use a different portal built by
        different business templates.
      """
      m = md5.new()
      m.update(repr(self.getBusinessTemplateList())+ self.getTitle())
      uid = m.hexdigest()

      return portal_name + '_' + uid

    def getPortal(self):
        """Returns the portal object, i.e. the "fixture root".
           Override if you don't like the default.
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
      uf._doAddUser('ERP5TypeTestCase', '', ['Manager', 'Member'], [])
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
        # This is a workaround for the overwriting problem in Testing/__init__.py in Zope.
        # So this overwrites them again to revert the changes made by Testing.
        try:
          import App.config
        except ImportError:
          os.environ['INSTANCE_HOME'] = INSTANCE_HOME = os.environ['COPY_OF_INSTANCE_HOME']
          os.environ['SOFTWARE_HOME'] = SOFTWARE_HOME = os.environ['COPY_OF_SOFTWARE_HOME']
        else:
          cfg = App.config.getConfiguration()
          cfg.instancehome = os.environ['COPY_OF_INSTANCE_HOME']
          App.config.setConfiguration(cfg)
        INSTANCE_HOME = os.environ['INSTANCE_HOME']

        template_list = self.getBusinessTemplateList()
        new_template_list = []
        LOG('template_list',0,template_list)
        for template in template_list:
          id = template
          try :
            from urllib import urlretrieve
            file, headers = urlretrieve(template)
          except IOError :
            from glob import glob
            template_list = glob(os.path.join(INSTANCE_HOME, 'bt5', '*', '%s' % template))
            if len(template_list) == 0:
              template_list = glob(os.path.join(INSTANCE_HOME, 'bt5', '*', '%s.bt5' % template))
            if not (len(template_list) and template_list[0]):
              template = '%s' % id
              if not os.path.exists(template):
                template = '%s.bt5' % id
            else:
              template = template_list[0]
          else :            
            template = '%s' % template
            if not os.path.exists(template):
              template = '%s.bt5' % template
          new_template_list.append((template,id))

        light_install = self.enableLightInstall()
        create_activities = self.enableActivityTool()
        hot_reindexing = self.enableHotReindexing()
        setupERP5Site(business_template_list = new_template_list,light_install=light_install,
                      portal_name = self.getPortalName(),title = self.getTitle(),
                      create_activities=create_activities,hot_reindexing=hot_reindexing)
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

    # Utility methods specific to ERP5Type
    def getTemplateTool(self):
        return getToolByName(self.getPortal(), 'portal_templates', None)
      
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

    def getTypeTool(self):
        return getToolByName(self.getPortal(), 'portal_types', None)

    def getRuleTool(self):
        return getattr(self.getPortal(), 'portal_rules', None)

    def getClassTool(self):
        return getattr(self.getPortal(), 'portal_classes', None)

    def getSimulationTool(self):
        return getToolByName(self.getPortal(), 'portal_simulation', None)

    def getSqlConnection(self):
        return getToolByName(self.getPortal(), 'erp5_sql_connection', None)

    def getPortalId(self):
      return self.getPortal().getId()

    def getDomainTool(self):
      return getToolByName(self.getPortal(), 'portal_domains', None)

    def getAlarmTool(self):
      return getattr(self.getPortal(), 'portal_alarms', None)

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
          portal_activities.distribute()
          portal_activities.tic()
          # This prevents an infinite loop.
          count -= 1
          if count == 0:
            raise RuntimeError, 'tic is looping forever. These messages are pending: %r' % ([('/'.join(m.object_path), m.method_id, m.processing_node, m.priority) for m in portal_activities.getMessageList()],)
          # This give some time between messages
          if count % 10 == 0:
            from Products.CMFActivity.Activity.Queue import VALIDATION_ERROR_DELAY
            portal_activities.timeShift(3 * VALIDATION_ERROR_DELAY)


    def failIfDifferentSet(self, a,b):
      LOG('failIfDifferentSet',0,'a:%s b:%s' % (repr(a),repr(b)))
      for i in a:
        self.failUnless(i in b)
      for i in b:
        self.failUnless(i in a)
      self.assertEquals(len(a),len(b))


def setupERP5Site(business_template_list=(), app=None, portal_name=portal_name, title='',quiet=0,
                  light_install=1,create_activities=1,hot_reindexing=1):
    '''
      Creates an ERP5 site.
      business_template_list must be specified correctly (e.g. '("erp5_common", )').
    '''
    try:
      if app is None:
        app = ZopeTestCase.app()
      if not hasattr(aq_base(app), portal_name):
          try:
            _start = time.time()
            # Add user and log in
            if not quiet: ZopeTestCase._print('\nAdding ERP5TypeTestCase user ... \n')
            uf = app.acl_users
            uf._doAddUser('ERP5TypeTestCase', '', ['Manager'], [])
            user = uf.getUserById('ERP5TypeTestCase').__of__(uf)
            newSecurityManager(None, user)
            # Add ERP5 Site
            #factory = app.manage_addProduct['CMFDefault']
            #factory.manage_addCMFSite(id)
            reindex = 1
            if hot_reindexing:
              setattr(app,'isIndexable',0)
              reindex = 0
            if not quiet: ZopeTestCase._print('Adding %s ERP5 Site ... \n' % portal_name)
            factory = app.manage_addProduct['ERP5'] # Not needed by ERP5Type
            factory.manage_addERP5Site(portal_name,light_install=light_install,
                reindex=reindex,create_activities=create_activities)
            # Release locks
            #get_transaction().commit()
            portal=app[portal_name]
            # Remove all local PropertySheets, Documents
            for id in getLocalPropertySheetList():
              removeLocalPropertySheet(id)
            for id in getLocalDocumentList():
              removeLocalDocument(id)
            for id in getLocalConstraintList():
              removeLocalConstraint(id)
            # Disable reindexing before adding templates
            # VERY IMPORTANT: Add some business templates
            for url,id in business_template_list:
              ZopeTestCase._print('Adding %s business template ... \n' % id)
              #portal.portal_templates.download('%s.zexp' % id, id=id)
              portal.portal_templates.download(url, id=id)
              portal.portal_templates[id].install(light_install=light_install)
              # Release locks
              #get_transaction().commit()
            # Enbable reindexing
            # Do hot reindexing # Does not work
            if hot_reindexing:
              setattr(app,'isIndexable',1)
              portal.portal_catalog.manage_hotReindexAll()

            get_transaction().commit()
            portal_activities = getattr(portal,'portal_activities',None)
            if portal_activities is not None:
              while len(portal_activities.getMessageList()) > 0:
                portal_activities.distribute()
                portal_activities.tic()
                get_transaction().commit()
            # Reset aq dynamic, so all unit tests will start again
            from Products.ERP5Type.Base import _aq_reset
            _aq_reset()
            # Log out
            if not quiet: ZopeTestCase._print('Logout ... \n')
            noSecurityManager()
            if not quiet: ZopeTestCase._print('done (%.3fs)\n' % (time.time()-_start,))
            if not quiet: ZopeTestCase._print('Ran Unit test of %s\n' % title)
          finally:
            get_transaction().commit()
            ZopeTestCase.close(app)
    except:
      f = StringIO()
      traceback.print_exc(file=f)
      ZopeTestCase._print(f.getvalue())
      f.close()


def optimize():
    '''Significantly reduces portal creation time.'''
    def __init__(self, text):
        # Don't compile expressions on creation
        self.text = text
    from Products.CMFCore.Expression import Expression
    Expression.__init__ = __init__
    def _cloneActions(self):
        # Don't clone actions but convert to list only
        return list(self._actions)
    from Products.CMFCore.ActionProviderBase import ActionProviderBase
    ActionProviderBase._cloneActions = _cloneActions

optimize()
