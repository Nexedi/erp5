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
ZopeTestCase.installProduct('CMFActivity')
ZopeTestCase.installProduct('ERP5Type')
ZopeTestCase.installProduct('ERP5Form') # Not required by ERP5Type but required by ERP5Form
ZopeTestCase.installProduct('ERP5SyncML')
ZopeTestCase.installProduct('ERP5') # Not needed by ERP5Type

from AccessControl.SecurityManagement import newSecurityManager, noSecurityManager
from AccessControl.User import User

from Acquisition import aq_base
import time

from Products.ERP5.ERP5Site import ERP5Site

portal_name = 'erp5_portal'

class ERP5TypeTestCase(PortalTestCase):

    def getPortal(self):
        '''Returns the portal object, i.e. the "fixture root".
           Override if you don't like the default.
        '''
        return self.app[portal_name]

    def setUp(self):
        '''Sets up the fixture. Do not override,
           use the hooks instead.
        '''
        PortalTestCase.setUp(self)
        self._buildERP5Site()

    def afterSetUp(self):
        '''Called after setUp() has completed. This is
           far and away the most useful hook.
        '''
        pass

    def _buildERP5Site(self):
        """
          ERP5 Specific - includes all steps to build a basic site
        """
        pass


def setupERP5Site(app, id='portal', quiet=0):
    '''Creates a ERP5 site.'''
    if not hasattr(aq_base(app), id):
        _start = time.time()
        # Add user and log in
        if not quiet: ZopeTestCase._print('Adding ERP5TypeTestCase user ... ')
        uf = app.acl_users
        uf._doAddUser('ERP5TypeTestCase', '', ['Manager'], [])
        user = uf.getUserById('ERP5TypeTestCase').__of__(uf)
        newSecurityManager(None, user)
        # Add ERP5 Site
        #factory = app.manage_addProduct['CMFDefault']
        #factory.manage_addCMFSite(id)
        if not quiet: ZopeTestCase._print('Adding ERP5 Site ... ')
        factory = app.manage_addProduct['ERP5'] # Not needed by ERP5Type
        factory.manage_addERP5Site(id)
        # Log out
        if not quiet: ZopeTestCase._print('Logout ... ')
        noSecurityManager()
        get_transaction().commit()
        if not quiet: ZopeTestCase._print('done (%.3fs)\n' % (time.time()-_start,))


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

# Create a ERP5 site in the test (demo-) storage
app = ZopeTestCase.app()
setupERP5Site(app, id=portal_name)
#print "Object Ids"
#print app.objectIds()
#print app.erp5.objectIds()
ZopeTestCase.close(app)

