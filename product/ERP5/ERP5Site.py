  ##############################################################################
#
# Copyright (c) 2001 Zope Corporation and Contributors. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE
#
##############################################################################
""" Portal class

$Id$
"""

import Globals
from Globals import package_home
#from Products.ERP5 import content_classes
from AccessControl import ClassSecurityInfo
from Products.CMFDefault.Portal import CMFSite, PortalGenerator
from Products.CMFCore.utils import getToolByName, _getAuthenticatedUser
from Products.ERP5Type import Permissions, PropertySheet, Constraint, Interface
from Products.ERP5Type.Document.Folder import FolderMixIn
from Products.ERP5Type.Document import addFolder
from Acquisition import aq_base, aq_parent, aq_inner, aq_acquire
from Products.ERP5Type import allowClassTool

import ERP5Defaults
from os import path

from zLOG import LOG
from string import join

import os

#factory_type_information = []
#for c in content_classes:
#  factory_type_information.append(getattr(c, 'factory_type_information', []))

# Site Creation DTML
manage_addERP5SiteForm = Globals.HTMLFile('dtml/addERP5Site', globals())
manage_addERP5SiteForm.__name__ = 'addERP5Site'

# ERP5Site Constructor
def manage_addERP5Site(self, id, title='ERP5', description='',
                         create_userfolder=1,
                         create_activities=1,
                         email_from_address='postmaster@localhost',
                         email_from_name='Portal Administrator',
                         validate_email=0,
                         erp5_sql_connection_type='Z MySQL Database Connection',
                         erp5_sql_connection_string='test test',
                         cmf_activity_sql_connection_type='Z MySQL Database Connection',
                         cmf_activity_sql_connection_string='test test',
                         light_install=0,reindex=1,
                         RESPONSE=None):
    '''
    Adds a portal instance.
    '''
    #LOG('manage_addERP5Site, create_activities',0,create_activities)
    #LOG('manage_addERP5Site, create_activities==1',0,create_activities==1)
    gen = ERP5Generator()
    from string import strip
    id = strip(id)
    p = gen.create(self, id, create_userfolder,
                   erp5_sql_connection_type,erp5_sql_connection_string,
                   cmf_activity_sql_connection_type,cmf_activity_sql_connection_string,
                   create_activities=create_activities,light_install=light_install,
                   reindex=reindex)
    gen.setupDefaultProperties(p, title, description,
                               email_from_address, email_from_name,
                               validate_email)
    if RESPONSE is not None:
        RESPONSE.redirect(p.absolute_url())

class ERP5Site ( CMFSite, FolderMixIn ):
    """
        The *only* function this class should have is to help in the setup
        of a new ERP5.  It should not assist in the functionality at all.
    """
    meta_type = 'ERP5 Site'
    constructors = (manage_addERP5SiteForm, manage_addERP5Site, )
    uid = 0
    last_id = 0
    icon = 'portal.gif'

    _properties = (
        {'id':'title', 'type':'string'},
        {'id':'description', 'type':'text'},
        )
    title = ''
    description = ''

    # Declarative security
    security = ClassSecurityInfo()
    security.declareObjectProtected(Permissions.View)

    security.declareProtected(Permissions.View, 'view')
    def view(self):
        """
          Returns the default view.
          Implemented for consistency
        """
        return self.index_html()

    security.declareProtected(Permissions.AccessContentsInformation, 'getPortalObject')
    def getPortalObject(self):
      return self

    security.declareProtected(Permissions.AccessContentsInformation, 'getTitle')
    def getTitle(self):
      """
        Return the title.
      """
      return self.title

    security.declareProtected(Permissions.AccessContentsInformation, 'getUid')
    def getUid(self):
      """
        Returns the UID of the object. Eventually reindexes
        the object in order to make sure there is a UID
        (useful for import / export).

        WARNING : must be updates for circular references issues
      """
      #if not hasattr(self, 'uid'):
      #  self.reindexObject()
      return getattr(self, 'uid', 0)

    security.declareProtected(Permissions.AccessContentsInformation, 'getParentUid')
    def getParentUid(self):
      """
        A portal has no parent
      """
      return self.getUid()

    # Required to allow content creation outside folders
    security.declareProtected(Permissions.View, 'getIdGroup')
    def getIdGroup(self):
      return None

    # Required to allow content creation outside folders
    security.declareProtected(Permissions.View, 'setLastId')
    def setLastId(self, id):
      self.last_id = id

    security.declareProtected(Permissions.AccessContentsInformation, 'getPath')
    def getPath(self, REQUEST=None):
      """
        Returns the absolute path of an object
      """
      return join(self.getPhysicalPath(),'/')

    security.declareProtected(Permissions.AccessContentsInformation, 'searchFolder')
    def searchFolder(self, **kw):
      """
        Search the content of a folder by calling
        the portal_catalog.
      """
      if not kw.has_key('parent_uid'):
        kw['parent_uid'] = self.uid
      kw2 = {}
      # Remove useless matter before calling the
      # catalog. In particular, consider empty
      # strings as None values
      for cname in kw.keys():
        if kw[cname] != '' and kw[cname]!=None:
          kw2[cname] = kw[cname]
      # The method to call to search the folder
      # content has to be called z_search_folder
      method = self.portal_catalog.searchResults
      return method(**kw2)

    security.declareProtected(Permissions.AccessContentsInformation, 'countFolder')
    def countFolder(self, **kw):
      """
        Count the content of a folder by calling
        the portal_catalog.
      """
      if not kw.has_key('parent_uid'):
        kw['parent_uid'] = self.uid
      kw2 = {}
      # Remove useless matter before calling the
      # catalog. In particular, consider empty
      # strings as None values
      for cname in kw.keys():
        if kw[cname] != '' and kw[cname]!=None:
          kw2[cname] = kw[cname]
      # The method to call to search the folder
      # content has to be called z_search_folder
      method = self.portal_catalog.countResults
      return method(**kw2)

    # Proxy methods for security reasons
    def getOwnerInfo(self):
      return self.owner_info()

    # Make sure fixConsistency is recursive - ERROR - this creates recursion errors
    # checkConsistency = Folder.checkConsistency
    # fixConsistency = Folder.fixConsistency

    security.declarePublic('getOrderedGlobalActionList')
    def getOrderedGlobalActionList(self, action_list):
      """
      Returns a dictionnary of actions, sorted by type of object

      This should absolutely be rewritten by using clean concepts to separate worklists XXX
      """
      #LOG("getOrderedGlobalActionList", 0, str(action_list))
      sorted_workflow_actions = {}
      sorted_global_actions = []
      other_global_actions = []
      for action in action_list:
        action['disabled'] = 0
        if action.has_key('workflow_title'):
          if not sorted_workflow_actions.has_key(action['workflow_title']):
            sorted_workflow_actions[action['workflow_title']] = []
          sorted_workflow_actions[action['workflow_title']].append(action)
        else:
          other_global_actions.append(action)
      workflow_title_list = sorted_workflow_actions.keys()
      workflow_title_list.sort()
      for key in workflow_title_list:
        sorted_global_actions.append({'title': key, 'disabled': 1})
        sorted_global_actions.extend(sorted_workflow_actions[key])
      sorted_global_actions.append({'title': 'Others', 'disabled': 1})
      sorted_global_actions.extend(other_global_actions)
      return sorted_global_actions

    def setupDefaultProperties(self, p, title, description,
                               email_from_address, email_from_name,
                               validate_email
                               ):
        CMFSite.setupDefaultProperties(self, p, title, description,
                               email_from_address, email_from_name,
                               validate_email)

    # Portal methods are based on the concept of having portal-specific parameters
    # for customization. In the past, we used global parameters, but it was not very good
    # because it was very difficult to customize the settings for each portal site.
    def _getPortalConfiguration(self, id):
      """
        Get a portal-specific configuration.

        Current implementation is using properties in a portal object.
        If not found, try to get a default value for backward compatibility.

        This implementation can be improved by gathering information from appropriate places,
        such as portal_types, portal_categories and portal_workflow.
      """
      if self.hasProperty(id):
        return self.getProperty(id)

      # Fall back to the default.
      return getattr(ERP5Defaults, id, None)

    security.declareProtected(Permissions.AccessContentsInformation, 'getPortalDefaultSectionCategory')
    def getPortalDefaultSectionCategory(self):
      """
        Return a default section category.
      """
      return self._getPortalConfiguration('portal_default_section_category')

    security.declareProtected(Permissions.AccessContentsInformation, 'getPortalResourceTypeList')
    def getPortalResourceTypeList(self):
      """
        Return resource types.
      """
      return self._getPortalConfiguration('portal_resource_type_list')

    security.declareProtected(Permissions.AccessContentsInformation, 'getPortalVariationTypeList')
    def getPortalVariationTypeList(self):
      """
        Return variation types.
      """
      return self._getPortalConfiguration('portal_variation_type_list')

    security.declareProtected(Permissions.AccessContentsInformation, 'getPortalNodeTypeList')
    def getPortalNodeTypeList(self):
      """
        Return node types.
      """
      return self._getPortalConfiguration('portal_node_type_list')

    security.declareProtected(Permissions.AccessContentsInformation, 'getPortalInvoiceTypeList')
    def getPortalInvoiceTypeList(self):
      """
        Return invoice types.
      """
      return self._getPortalConfiguration('portal_invoice_type_list')

    security.declareProtected(Permissions.AccessContentsInformation, 'getPortalOrderTypeList')
    def getPortalOrderTypeList(self):
      """
        Return order types.
      """
      return self._getPortalConfiguration('portal_order_type_list')

    security.declareProtected(Permissions.AccessContentsInformation, 'getPortalDefaultCollection')
    def getPortalDefaultCollection(self):
      """
        Return order types.
      """
      return self._getPortalConfiguration('portal_default_collection')

    security.declareProtected(Permissions.AccessContentsInformation, 'getPortalDeliveryTypeList')
    def getPortalDeliveryTypeList(self):
      """
        Return delivery types.
      """
      return self._getPortalConfiguration('portal_delivery_type_list')

    security.declareProtected(Permissions.AccessContentsInformation, 'getPortalVariationBaseCategoryList')
    def getPortalVariationBaseCategoryList(self):
      """
        Return variation base categories.
      """
      return self._getPortalConfiguration('portal_variation_base_category_list')

    security.declareProtected(Permissions.AccessContentsInformation, 'getPortalInvoiceMovementTypeList')
    def getPortalInvoiceMovementTypeList(self):
      """
        Return invoice movement types.
      """
      return self._getPortalConfiguration('portal_invoice_movement_type_list')

    security.declareProtected(Permissions.AccessContentsInformation, 'getPortalOrderMovementTypeList')
    def getPortalOrderMovementTypeList(self):
      """
        Return order movement types.
      """
      return self._getPortalConfiguration('portal_order_movement_type_list')

    security.declareProtected(Permissions.AccessContentsInformation, 'getPortalDeliveryMovementTypeList')
    def getPortalDeliveryMovementTypeList(self):
      """
        Return delivery movement types.
      """
      return self._getPortalConfiguration('portal_delivery_movement_type_list')

    security.declareProtected(Permissions.AccessContentsInformation, 'getPortalAcquisitionMovementTypeList')
    def getPortalAcquisitionMovementTypeList(self):
      """
        Return acquisition movement types.
      """
      return tuple(list(self.getPortalOrderMovementTypeList()) + list(self.getPortalDeliveryMovementTypeList()) + list(self.getPortalInvoiceMovementTypeList()))

    security.declareProtected(Permissions.AccessContentsInformation, 'getPortalMovementTypeList')
    def getPortalMovementTypeList(self):
      """
        Return movement types.
      """
      return tuple(list(self.getPortalOrderMovementTypeList()) + list(self.getPortalDeliveryMovementTypeList()) + list(self.getPortalInvoiceMovementTypeList()) + ['Simulation Movement'])

    security.declareProtected(Permissions.AccessContentsInformation, 'getPortalSimulatedMovementTypeList')
    def getPortalSimulatedMovementTypeList(self):
      """
        Return simulated movement types.
      """
      return tuple(filter(lambda x: x != 'Container Line' and x != 'Container Cell', self.getPortalMovementTypeList()))

    security.declareProtected(Permissions.AccessContentsInformation, 'getPortalContainerTypeList')
    def getPortalContainerTypeList(self):
      """
        Return container types.
      """
      return self._getPortalConfiguration('portal_container_type_list')

    security.declareProtected(Permissions.AccessContentsInformation, 'getPortalContainerLineTypeList')
    def getPortalContainerLineTypeList(self):
      """
        Return container line types.
      """
      return self._getPortalConfiguration('portal_container_line_type_list')

    security.declareProtected(Permissions.AccessContentsInformation, 'getPortalItemTypeList')
    def getPortalItemTypeList(self):
      """
        Return item types.
      """
      return self._getPortalConfiguration('portal_item_type_list')

    security.declareProtected(Permissions.AccessContentsInformation, 'getPortalDiscountTypeList')
    def getPortalDiscountTypeList(self):
      """
        Return discount types.
      """
      return self._getPortalConfiguration('portal_discount_type_list')

    security.declareProtected(Permissions.AccessContentsInformation, 'getPortalAlarmTypeList')
    def getPortalAlarmTypeList(self):
      """
        Return alarm types.
      """
      return self._getPortalConfiguration('portal_alarm_type_list')

    security.declareProtected(Permissions.AccessContentsInformation, 'getPortalPaymentConditionTypeList')
    def getPortalPaymentConditionTypeList(self):
      """
        Return payment condition types.
      """
      return self._getPortalConfiguration('portal_payment_condition_type_list')

    security.declareProtected(Permissions.AccessContentsInformation, 'getPortalBalanceTransactionLineTypeList')
    def getPortalBalanceTransactionLineTypeList(self):
      """
        Return balance transaction line types.
      """
      return self._getPortalConfiguration('portal_balance_transaction_line_type_list')

    security.declareProtected(Permissions.AccessContentsInformation, 'getPortalCurrentInventoryStateList')
    def getPortalCurrentInventoryStateList(self):
      """
        Return current inventory states.
      """
      return self._getPortalConfiguration('portal_current_inventory_state_list')

    security.declareProtected(Permissions.AccessContentsInformation, 'getPortalTargetInventoryStateList')
    def getPortalTargetInventoryStateList(self):
      """
        Return target inventory states.
      """
      return self._getPortalConfiguration('portal_target_inventory_state_list')

    security.declareProtected(Permissions.AccessContentsInformation, 'getPortalDraftOrderStateList')
    def getPortalDraftOrderStateList(self):
      """
        Return draft order states.
      """
      return self._getPortalConfiguration('portal_draft_order_state_list')

    security.declareProtected(Permissions.AccessContentsInformation, 'getPortalPlannedOrderStateList')
    def getPortalPlannedOrderStateList(self):
      """
        Return planned order states.
      """
      return self._getPortalConfiguration('portal_planned_order_state_list')

    security.declareProtected(Permissions.AccessContentsInformation, 'getPortalReservedInventoryStateList')
    def getPortalReservedInventoryStateList(self):
      """
        Return reserved inventory states.
      """
      return self._getPortalConfiguration('portal_reserved_inventory_state_list')

    security.declareProtected(Permissions.AccessContentsInformation, 'getPortalFutureInventoryStateList')
    def getPortalFutureInventoryStateList(self):
      """
        Return future inventory states.
      """
      return self._getPortalConfiguration('portal_future_inventory_state_list')

    security.declareProtected(Permissions.AccessContentsInformation, 'getPortalColumnBaseCategoryList')
    def getPortalColumnBaseCategoryList(self):
      """
        Return column base categories.
      """
      return self._getPortalConfiguration('portal_column_base_category_list')

    security.declareProtected(Permissions.AccessContentsInformation, 'getPortalLineBaseCategoryList')
    def getPortalLineBaseCategoryList(self):
      """
        Return line base categories.
      """
      return self._getPortalConfiguration('portal_line_base_category_list')

    security.declareProtected(Permissions.AccessContentsInformation, 'getPortalTabBaseCategoryList')
    def getPortalTabBaseCategoryList(self):
      """
        Return tab base categories.
      """
      return self._getPortalConfiguration('portal_tab_base_category_list')

    
    security.declareProtected(Permissions.AccessContentsInformation, 'getDefaultModuleId')
    def getDefaultModuleId(self, portal_type):
      """
        Return default module id where a object with portal_type can be created
      """
      # XXX very dummy method, but it works with today name convention
      module_name = portal_type.lower().replace(' ','_')

      portal_object = self
      if not hasattr(portal_object, module_name):
        module_name += '_module'
        if not hasattr(portal_object, module_name):
          LOG('ERP5Site, getDefaultModuleId',0,'Unable to find default module for portal_type: %s' % portal_type )
          raise
      return module_name

    security.declareProtected(Permissions.AccessContentsInformation, 'getDefaultModule')
    def getDefaultModule(self, portal_type):
      """
        Return default module where a object with portal_type can be created
      """
      return getattr(self, self.getDefaultModuleId(portal_type), None)

    security.declareProtected(Permissions.AddPortalContent, 'newContent')
    def newContent(self, id=None, portal_type=None, immediate_reindex=0, **kw):
      """
        Creates a new content
      """
      if id is None:
        raise ValueError, 'The id should not be None'
      if portal_type is None:
        raise ValueError, 'The portal_type should not be None'
      self.portal_types.constructContent(type_name=portal_type,
                                         container=self,
                                         id=id,
                                         ) # **kw) removed due to CMF bug
      new_instance = self[id]
      if kw is not None: new_instance._edit(force_update=1, **kw)
      if immediate_reindex: new_instance.immediateReindexObject()
      return new_instance


Globals.InitializeClass(ERP5Site)

class ERP5Generator(PortalGenerator):

    klass = ERP5Site

    def getBootstrapDirectory(self):
        """
          Return the name of the bootstrap directory
        """
        product_path = package_home(globals())
        return os.path.join(product_path, 'bootstrap')

    def create(self, parent, id, create_userfolder,
               erp5_sql_connection_type, erp5_sql_connection_string,
               cmf_activity_sql_connection_type,cmf_activity_sql_connection_string,
               reindex=1,**kw):
        LOG('setupTools, create',0,kw)
        id = str(id)
        portal = self.klass(id=id)
        if reindex==0:
          setattr(portal,'isIndexable',0)
        parent._setObject(id, portal)
        # Return the fully wrapped object.
        p = parent.this()._getOb(id)
        p._setProperty('erp5_sql_connection_type', erp5_sql_connection_type, 'string')
        p._setProperty('erp5_sql_connection_string', erp5_sql_connection_string, 'string')
        p._setProperty('cmf_activity_sql_connection_type', cmf_activity_sql_connection_type, 'string')
        p._setProperty('cmf_activity_sql_connection_string', cmf_activity_sql_connection_string, 'string')
        p._setProperty('management_page_charset', 'UTF-8', 'string') # XXX hardcoded charset
        self.setup(p, create_userfolder,**kw)
        return p

    def setupLastTools(self, p,**kw):
        """Set up finals tools
           We want to set the activity tool only at the end to
           make sure that we do not put un the queue the full reindexation
        """
        # Add Activity Tool
        LOG('setupTools, kw',0,kw)
        if kw.has_key('create_activities') and int(kw['create_activities'])==1:
          addTool = p.manage_addProduct['CMFActivity'].manage_addTool
          addTool('CMF Activity Tool', None) # Allow user to select active/passive

    def setupTools(self, p,**kw):
        """Set up initial tools"""

        if not 'portal_actions' in p.objectIds():
          PortalGenerator.setupTools(self, p)

        # Add CMF Report Tool
        addTool = p.manage_addProduct['CMFReportTool'].manage_addTool
        addTool('CMF Report Tool', None)

        # Add ERP5 Tools
        addTool = p.manage_addProduct['ERP5'].manage_addTool
        #print "addTool = %s" % str(addTool)
        addTool('ERP5 Categories', None)
        addTool('ERP5 Rule Tool', None)
        addTool('ERP5 Id Tool', None)
        addTool('ERP5 Simulation Tool', None)
        addTool('ERP5 Template Tool', None)
        addTool('ERP5 Alarm Tool', None)
        addTool('ERP5 Domain Tool', None)
        addTool('ERP5 Delivery Tool', None)

        # Add ERP5Type Tools
        addTool = p.manage_addProduct['ERP5Type'].manage_addTool
        if allowClassTool():
          addTool('ERP5 Class Tool', None)
        else:
          addTool('ERP5 Dummy Class Tool', None)

        # Add ERP5 SQL Catalog Tool
        addTool = p.manage_addProduct['ERP5Catalog'].manage_addTool
        p._delObject('portal_catalog')
        addTool('ERP5 Catalog', None)
        # Add Default SQL connection
        if p.erp5_sql_connection_type == 'Z MySQL Database Connection':
          addSQLConnection = p.manage_addProduct['ZSQLMethods'].manage_addZMySQLConnection
          addSQLConnection('erp5_sql_connection', 'ERP5 SQL Server Connection', p.erp5_sql_connection_string)
        elif p.erp5_sql_connection_type == 'Z Gadfly':
          pass
        if p.cmf_activity_sql_connection_type == 'Z MySQL Database Connection':
          addSQLConnection = p.manage_addProduct['ZSQLMethods'].manage_addZMySQLConnection
          addSQLConnection('cmf_activity_sql_connection', 'CMF Activity SQL Server Connection', p.cmf_activity_sql_connection_string)
        elif p.cmf_activity_sql_connection_type == 'Z Gadfly':
          pass
        # Create default methods in Catalog XXX
        portal_catalog = getToolByName(p, 'portal_catalog')
        portal_catalog.addDefaultSQLMethods('erp5_mysql')

        # Clear Catalog
        portal_catalog.manage_catalogClear()

        # Add Selection Tool
        addTool = p.manage_addProduct['ERP5Form'].manage_addTool
        addTool('ERP5 Selections', None)

        # Add ERP5SyncML Tools
        addTool = p.manage_addProduct['ERP5SyncML'].manage_addTool
        addTool('ERP5 Synchronizations', None)

        # Add Message Catalog
        #if 'Localizer' in p.objectIds():
          #p._delObject('Localizer') # Why delete it, we should keep for ERP5/CPS
        if not 'Localizer' in p.objectIds():
          #p._delObject('Localizer') # Why delete it, we should keep for ERP5/CPS
          addLocalizer = p.manage_addProduct['Localizer'].manage_addLocalizer
          addLocalizer('', ('en',))
        localizer = getToolByName(p, 'Localizer')
        addMessageCatalog = localizer.manage_addProduct['Localizer'].manage_addMessageCatalog
        if 'default' in localizer.objectIds():
          localizer.manage_delObjects('default')
        addMessageCatalog('default', 'ERP5 Localized Messages', ('en',))
        addMessageCatalog('erp5_ui', 'ERP5 Localized Interface', ('en',))
        addMessageCatalog('erp5_content', 'ERP5 Localized Content', ('en',))

        # Add Translation Service
        if 'translation_service' in p.objectIds():
          p._delObject('translation_service')
        p.manage_addProduct['TranslationService'].addPlacefulTranslationService('translation_service')
        p.translation_service.manage_setDomainInfo(domain_0=None, path_0='Localizer/default')
        p.translation_service.manage_addDomainInfo(domain='ui', path='Localizer/erp5_ui')
        p.translation_service.manage_addDomainInfo(domain='content', path='Localizer/erp5_content')


    def setupMembersFolder(self, p):
        """
          ERP5 is not a CMS
        """
        pass
        #from Products.CMFDefault.MembershipTool import MembershipTool
        #addFolder(p, id=MembershipTool.membersfolder_id, title='ERP5 Members')
        #member_folder = p[MembershipTool.membersfolder_id]
        #member_folder.manage_addProduct['OFSP'].manage_addDTMLMethod(
        #    'index_html', 'Member list', '<dtml-return roster>')

    def setupFrontPage(self, p):
        text = """<span metal:define-macro="body">

  <span tal:condition="python: not here.portal_membership.isAnonymousUser()">
    <br/>
    <br/>
    <br/>
    <br/>
    <h2 align="center" i18n:translate="" i18n:domain="ui">
      Welcome to ERP5
    </h2>
    <table border="1" align="center">
      <tr tal:define="module_list python:here.ERP5Site_getModuleItemList();
                      module_len python:len(module_list);
                      col_size python:16;
                      col_len python:(module_len + col_size) / col_size">
        <td>
          <img src="images/erp5_logo.jpg" alt="ERP5 Logo" />
        </td>
        <tal:block tal:repeat="col_no python:range(col_len)">
          <td valign="top" class="ModuleShortcut">
            <tal:block tal:repeat="module python:module_list[col_size*col_no:min(col_size*(col_no+1),module_len)] ">
              <p>
                <a href="person"
                  tal:content="python: module[1]"
                  tal:attributes="href python: module[0] + '/view'">
                  Person
                </a>
              </p>
            </tal:block>
          </td>
        </tal:block>
      </tr>
    </table>
  </span>

  <span tal:condition="python: here.portal_membership.isAnonymousUser()">
    <p tal:define="dummy python:request.RESPONSE.redirect('%s/login_form' % here.absolute_url())"/>
  </span>

</span>
"""
        p.manage_addProduct['PageTemplates'].manage_addPageTemplate(
                  'local_pt', title='ERP5 Front Page', text=text)

    def setupDefaultSkins(self, p):
        from Products.CMFCore.DirectoryView import addDirectoryViews
        from Products.CMFDefault import cmfdefault_globals
        from Products.CMFActivity import cmfactivity_globals
        ps = getToolByName(p, 'portal_skins')
        # Do not use filesystem skins for ERP5 any longer.
        # addDirectoryViews(ps, 'skins', globals())
        # addDirectoryViews(ps, path.join('skins','pro'), globals())
        addDirectoryViews(ps, 'skins', cmfdefault_globals)
        addDirectoryViews(ps, 'skins', cmfactivity_globals)
        ps.manage_addProduct['OFSP'].manage_addFolder(id='external_method')
        ps.manage_addProduct['OFSP'].manage_addFolder(id='custom')
        #ps.manage_addProduct['OFSP'].manage_addFolder(id='local_pro')
        #ps.manage_addProduct['OFSP'].manage_addFolder(id='local_mrp')
        ps.addSkinSelection('View', 'custom, external_method, activity, '
                                  + 'zpt_content, zpt_generic,'
                                  + 'zpt_control, content, generic, control, Images',
                            make_default=1)
        ps.addSkinSelection('Print', 'custom, external_method, activity, '
                                  + 'zpt_content, zpt_generic,'
                                  + 'zpt_control, content, generic, control, Images',
                            make_default=0)
        ps.addSkinSelection('CSV', 'custom, external_method, activity, '
                                  + 'zpt_content, zpt_generic,'
                                  + 'zpt_control, content, generic, control, Images',
                            make_default=0)
        p.setupCurrentSkin()

    def setupWorkflow(self, p):
        """
          Set up workflows for business templates
        """
        tool = getToolByName(p, 'portal_workflow', None)
        if tool is None:
            return
        bootstrap_dir = self.getBootstrapDirectory()
        business_template_building_workflow = os.path.join(bootstrap_dir,
                                                           'business_template_building_workflow.xml')
        tool._importObjectFromFile(business_template_building_workflow)
        business_template_installation_workflow = os.path.join(bootstrap_dir,
                                                               'business_template_installation_workflow.xml')
        tool._importObjectFromFile(business_template_installation_workflow)

        tool.setChainForPortalTypes( ( 'Business Template', ),
                                     ( 'business_template_building_workflow',
                                       'business_template_installation_workflow' ) )
        pass

    def setupIndex(self, p,**kw):
        from Products.CMFDefault.MembershipTool import MembershipTool
        # Make sure all tools and folders have been indexed
        portal_catalog = p.portal_catalog
        portal_catalog.manage_catalogClear()
        if kw.has_key('reindex') and kw['reindex']==0:
          return
        #portal_catalog.reindexObject(p)
        #portal_catalog.reindexObject(p.portal_templates)
        #portal_catalog.reindexObject(p.portal_categories)
        # portal_catalog.reindexObject(p.portal_activities)
        #p[MembershipTool.membersfolder_id].immediateReindexObject()
        skins_tool = getToolByName(p, 'portal_skins', None)
        if skins_tool is None:
          return
        skins_tool["erp5_core"].ERP5Site_reindexAll()

    def setupUserFolder(self, p):
        try:
          # Use NuxUserGroups instead of the standard acl_users.
          p.manage_addProduct['NuxUserGroups'].addUserFolderWithGroups()
        except:
          # No way.
          PortalGenerator.setupUserFolder(self, p)

    def setupPermissions(self, p):
      permission_dict = {
        'Access Transient Objects'     : ('Manager', 'Anonymous'),
        'Access contents information'  : ('Manager', 'Member', 'Anonymous'),
        'Access future portal content' : ('Manager', 'Reviewer'),
        'Access session data'          : ('Manager', 'Anonymous'),
        'AccessContentsInformation'    : ('Manager', 'Member'),
        'Add portal content'           : ('Manager', 'Owner'),
        'Add portal folders'           : ('Manager', 'Owner'),
        'Delete objects'               : ('Manager', 'Owner'),
        'FTP access'                   : ('Manager', 'Owner'),
        'List folder contents'         : ('Manager', 'Member'),
        'List portal members'          : ('Manager', 'Member'),
        'List undoable changes'        : ('Manager', 'Member'),
        'Manage properties'            : ('Manager', 'Owner'),
        'Modify portal content'        : ('Manager', 'Owner'),
        'Reply to item'                : ('Manager', 'Member'),
        'Review portal content'        : ('Manager', 'Reviewer'),
        'Search ZCatalog'              : ('Manager', 'Member'),
        'Set own password'             : ('Manager', 'Member'),
        'Set own properties'           : ('Manager', 'Member'),
        'Undo changes'                 : ('Manager', 'Owner'),
        'View'                         : ('Manager', 'Member', 'Owner', 'Anonymous'),
        'View management screens'      : ('Manager', 'Owner')
      }

      for permission in p.ac_inherited_permissions(1):
        name = permission[0]
        role_list = permission_dict.get(name, ('Manager',))
        p.manage_permission(name, roles=role_list, acquire=0)

    def setup(self, p, create_userfolder,**kw):
        self.setupTools(p,**kw)
        self.setupMailHost(p)
        if int(create_userfolder) != 0:
            self.setupUserFolder(p)
        self.setupCookieAuth(p)
        self.setupRoles(p)
        self.setupPermissions(p)
        self.setupDefaultSkins(p)

        # Initialize Activities
        portal_skins = p.portal_skins
        try:
          portal_skins.activity.SQLDict_dropMessageTable()
          portal_skins.activity.SQLQueue_dropMessageTable()
        except:
          pass
        portal_skins.activity.SQLDict_createMessageTable()
        portal_skins.activity.SQLQueue_createMessageTable()

        # Finish setup
        self.setupMembersFolder(p)

        # ERP5 Design Choice is that all content should be user defined
        # Content is disseminated through business templates
        self.setupBusinessTemplate(p)

        self.setupMimetypes(p)
        self.setupWorkflow(p)
        self.setupFrontPage(p)

        self.setupERP5Core(p,**kw)

        # Make sure tools are cleanly indexed with a uid before creating children
        # XXX for some strange reason, member was indexed 5 times
        self.setupIndex(p,**kw)

        self.setupLastTools(p,**kw)

    def setupBusinessTemplate(self,p):
        """
        Install the portal_type of Business Template
        """
        from Products.ERP5Type.ERP5Type import ERP5TypeInformation
        from Products.ERP5.Document.BusinessTemplate import BusinessTemplate
        tool = getToolByName(p, 'portal_types', None)
        if tool is None:
          return
        t = BusinessTemplate.factory_type_information
        ti = apply(ERP5TypeInformation, (), t)
        tool._setObject(t['id'], ti)

    def setupERP5Core(self,p,**kw):
        """
        Install the core part of ERP5
        """
        template_tool = getToolByName(p, 'portal_templates', None)
        if template_tool is None:
          return
        bootstrap_dir = self.getBootstrapDirectory()
        template = os.path.join(bootstrap_dir, 'erp5_core.bt5')

        id = template_tool.generateNewId()
        template_tool.download(template, id=id)
        template_tool[id].install(**kw)

# Patch the standard method
CMFSite.getPhysicalPath = ERP5Site.getPhysicalPath
