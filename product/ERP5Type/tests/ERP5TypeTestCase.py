# Derived from PloneTestCase in Plone.

#
# ERP5TypeTestCase
#

__version__ = '0.3.0'

from Testing import ZopeTestCase
from Testing.ZopeTestCase.PortalTestCase import PortalTestCase

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

# CMF
ZopeTestCase.installProduct('CMFCore')
ZopeTestCase.installProduct('CMFDefault')
ZopeTestCase.installProduct('CMFTopic')
ZopeTestCase.installProduct('DCWorkflow')
ZopeTestCase.installProduct('CMFCalendar')
ZopeTestCase.installProduct('CMFWiki')

# Based on CMF
ZopeTestCase.installProduct('CMFPhoto')
ZopeTestCase.installProduct('BTreeFolder2')
ZopeTestCase.installProduct('Base18')
ZopeTestCase.installProduct('CMFReportTool') # Not required by ERP5Type but required by ERP5Form
ZopeTestCase.installProduct('CMFMailIn')
ZopeTestCase.installProduct('TranslationService')

# ERP5
ZopeTestCase.installProduct('ERP5Catalog')
ZopeTestCase.installProduct('CMFCategory')
ZopeTestCase.installProduct('ERP5Type')
ZopeTestCase.installProduct('ERP5Form') # Not required by ERP5Type but required by ERP5Form
ZopeTestCase.installProduct('CMFActivity')
ZopeTestCase.installProduct('ERP5SyncML')
ZopeTestCase.installProduct('ERP5') # Not needed by ERP5Type

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

    def getPortalName(self):
      """
        Return the name of a portal for this test case.
        This is necessary for each test case to use a different portal built by
        different business templates.
      """
      m = md5.new()
      m.update(repr(self.getBusinessTemplateList()))
      uid = m.hexdigest()

      return portal_name + '_' + uid

    def getPortal(self):
        '''Returns the portal object, i.e. the "fixture root".
           Override if you don't like the default.
        '''
        return self.app[self.getPortalName()]

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

        setupERP5Site(business_template_list = self.getBusinessTemplateList(),
                      portal_name = self.getPortalName())
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
        return getattr(self.getPortal(), 'portal_templates', None)

    def getCategoryTool(self):
        return getattr(self.getPortal(), 'portal_categories', None)

    def getTypeTool(self):
        return getattr(self.getPortal(), 'portal_types', None)


def setupERP5Site(business_template_list=(), app=None, portal_name=portal_name, quiet=0):
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
            if not quiet: ZopeTestCase._print('Adding %s ERP5 Site ... \n' % portal_name)
            factory = app.manage_addProduct['ERP5'] # Not needed by ERP5Type
            factory.manage_addERP5Site(portal_name)
            portal=app[portal_name]
            # VERY IMPORTANT: Add some business templates
            for id in business_template_list:
              ZopeTestCase._print('Adding %s business template ... \n' % id)
              portal.portal_templates.download('%s.zexp' % id, id=id)
              portal.portal_templates[id].install()
            # Log out
            if not quiet: ZopeTestCase._print('Logout ... \n')
            noSecurityManager()
            if not quiet: ZopeTestCase._print('done (%.3fs)\n' % (time.time()-_start,))
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
