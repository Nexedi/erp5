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
"""
  Portal class
"""

import Globals
import AccessControl
from Globals import package_home

from Products.SiteErrorLog.SiteErrorLog import manage_addErrorLog
from ZPublisher import BeforeTraverse
from AccessControl import ClassSecurityInfo
from Products.CMFDefault.Portal import CMFSite, PortalGenerator
from Products.CMFCore.utils import getToolByName, _getAuthenticatedUser
from Products.ERP5Type import Permissions, PropertySheet, Constraint
from Products.ERP5Type.Core.Folder import FolderMixIn
from Acquisition import aq_base, aq_parent, aq_inner, aq_acquire
from Products.ERP5Type import allowClassTool
from Products.ERP5Type.Cache import CachingMethod
from Products.ERP5Type.ERP5Type import ERP5TypeInformation
from Products.ERP5.Document.BusinessTemplate import BusinessTemplate
from Products.ERP5Type.Log import log as unrestrictedLog
from Products.CMFActivity.Errors import ActivityPendingError
import ERP5Defaults
from Products.ERP5Type.TransactionalVariable import getTransactionalVariable

from zLOG import LOG, INFO
from string import join
import os, traceback
import warnings
import transaction
MARKER = []


# Site Creation DTML
manage_addERP5SiteFormDtml = Globals.HTMLFile('dtml/addERP5Site', globals())

def manage_addERP5SiteForm(*args, **kw):
  """
    Make getCatalogStorageList available from inside the dtml.
  """
  kw['getCatalogStorageList'] = getCatalogStorageList
  return manage_addERP5SiteFormDtml(*args, **kw)

# ERP5Site Constructor
def manage_addERP5Site(self,
                       id,
                       title='ERP5',
                       description='',
                       create_userfolder=1,
                       create_activities=1,
                       email_from_address='postmaster@localhost',
                       email_from_name='Portal Administrator',
                       validate_email=0,
                       erp5_catalog_storage='',
                       erp5_sql_connection_type='Z MySQL Database Connection',
                       erp5_sql_connection_string='test test',
                       erp5_sql_deferred_connection_type=\
                           'Z MySQL Deferred Database Connection',
                       cmf_activity_sql_connection_type= \
                           'Z MySQL Database Connection',
                       cmf_activity_sql_connection_string='test test',
                       light_install=0,
                       reindex=1,
                       RESPONSE=None):
  '''
  Adds a portal instance.
  '''
  gen = ERP5Generator()
  id = str(id).strip()
  p = gen.create(self,
                 id,
                 create_userfolder,
                 erp5_catalog_storage,
                 erp5_sql_connection_type,
                 erp5_sql_connection_string,
                 erp5_sql_deferred_connection_type,
                 cmf_activity_sql_connection_type,
                 cmf_activity_sql_connection_string,
                 create_activities=create_activities,
                 light_install=light_install,
                 reindex=reindex)
  gen.setupDefaultProperties(p,
                             title,
                             description,
                             email_from_address,
                             email_from_name,
                             validate_email)
  if RESPONSE is not None:
    RESPONSE.redirect(p.absolute_url())

def getCatalogStorageList(*args, **kw):
  """
    Returns the list of business templates available at install which can be
    used to setup a catalog storage.
  """
  result = []
  bootstrap_dir = getBootstrapDirectory()
  for item in os.listdir(bootstrap_dir):
    if item == '.svn':
      continue
    if item.endswith('.bt5') and os.path.isfile(item):
      # Simple heuristic to make it faster than extracting the whole bt
      if item.endswith('_catalog.bt5'):
        result.append((item, item))
    elif os.path.isdir(os.path.join(bootstrap_dir, item)):
      # Find if the business temlate provides erp5_catalog
      try:
        provides_file = open(os.path.join(bootstrap_dir, item, 'bt', 'provision_list'), 'r')
        provides_list = provides_file.readlines()
        provides_file.close()
      except IOError:
        provides_list = []
      if 'erp5_catalog' in provides_list:
        # Get a nice title (the first line of the description).
        try:
          title_file = open(os.path.join(bootstrap_dir, item, 'bt', 'description'), 'r')
          title = title_file.readline()
          title_file.close()
        except IOError:
          title = item
        result.append((item, title))
  return result

class ReferCheckerBeforeTraverseHook:
  """This before traverse hook checks the HTTP_REFERER argument in the request
  and refuses access to anything else that portal_url.

  This is enabled by calling the method enableRefererCheck on the portal.
  """
  handle = '_erp5_referer_check'

  def __call__(self, container, request):
    """Checks the request contains a valid referrer.
    """
    response = request.RESPONSE
    http_url = request.get('ACTUAL_URL', '').strip()
    http_referer = request.get('HTTP_REFERER', '').strip()

    user_password = request._authUserPW()
    if user_password:
      user = container.acl_users.getUserById(user_password[0]) or\
              container.aq_parent.acl_users.getUserById(user_password[0])
      # Manager can do anything
      if user is not None and 'Manager' in user.getRoles():
        return

    portal_url = container.portal_url.getPortalObject().absolute_url()
    if http_referer != '':
      # if HTTP_REFERER is set, user can acces the object if referer is ok
      if http_referer.startswith(portal_url):
        return
      LOG('HTTP_REFERER_CHECK : BAD REFERER !', INFO,
          'request : "%s", referer : "%s"' % (http_url, http_referer))
      response.unauthorized()
    else:
      # no HTTP_REFERER, we only allow to reach portal_url
      for i in ('/', '/index_html', '/login_form', '/view'):
        if http_url.endswith(i):
          http_url = http_url[:-len(i)]
          break
      if len(http_url) == 0 or not portal_url.startswith(http_url):
        LOG('HTTP_REFERER_CHECK : NO REFERER !', INFO,
            'request : "%s"' % http_url)
        response.unauthorized()

class ERP5Site(FolderMixIn, CMFSite):
  """
  The *only* function this class should have is to help in the setup
  of a new ERP5.  It should not assist in the functionality at all.
  """
  meta_type = 'ERP5 Site'
  portal_type = 'ERP5 Site'
  constructors = (('addERP5Site', manage_addERP5SiteForm), manage_addERP5Site, )
  uid = 0
  last_id = 0
  icon = 'portal.gif'
  isIndexable = 1 # Default value, prevents error during upgrade

  _properties = (
      { 'id':'title',
        'type':'string'},
      { 'id':'description',
        'type':'text'},
      )
  title = ''
  description = ''

  # Declarative security
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  security.declareProtected(Permissions.View, 'view')
  def view(self):
    """
      Returns the default view.
      Implemented for consistency
    """
    return self.index_html()

  security.declareProtected( Permissions.ModifyPortalContent, 'manage_renameObject' )
  def manage_renameObject(self, id=None, new_id=None, REQUEST=None):
    """manage renaming an object while keeping coherency for contained
    and linked to objects inside the renamed object.

    XXX this is nearly a copy-and-paste from CopySupport.

    XXX this is not good enough when the module or the objects inside
    the module are referred to by outer objects. But addressing this problem
    requires a full traversal of the object tree, and the current
    implementation is not efficient enough for this.
    """
    ob = self.restrictedTraverse(id)
    if getattr(aq_base(ob), '_updateInternalRelatedContent', None) is not None:
      # Make sure there is no activities pending on that object
      try:
        portal_activities = getToolByName(self, 'portal_activities')
      except AttributeError:
        # There is no activity tool
        portal_activities = None
      if portal_activities is not None:
        if portal_activities.countMessage(path=ob.getPath())>0:
          raise ActivityPendingError, 'Sorry, pending activities prevent ' \
                         +  'changing id at this current stage'

      # Search for categories that have to be updated in sub objects.
      ob._recursiveSetActivityAfterTag(ob)
      path_item_list = ob.getRelativeUrl().split('/')
      ob._updateInternalRelatedContent(object=ob,
                                       path_item_list=path_item_list,
                                       new_id=new_id)
    # Rename the object
    return CMFSite.manage_renameObject(self, id=id, new_id=new_id,
                                       REQUEST=REQUEST)

  def _getAcquireLocalRoles(self):
    """
      Prevent local roles from being acquired outside of Portal object.
      See ERP5Security/__init__.py:mergedLocalRoles .
    """
    return False

  security.declareProtected(Permissions.ManagePortal, 'enableRefererCheck')
  def enableRefererCheck(self):
    """Enable a ReferCheckerBeforeTraverseHook to check users have valid
    HTTP_REFERER
    """
    BeforeTraverse.registerBeforeTraverse(self,
                                        ReferCheckerBeforeTraverseHook(),
                                        ReferCheckerBeforeTraverseHook.handle,
                             # we want to be registered _after_ CookieCrumbler
                                        100)

  def _disableRefererCheck(self):
    """Disable the HTTP_REFERER check."""
    BeforeTraverse.unregisterBeforeTraverse(self,
                                        ReferCheckerBeforeTraverseHook.handle)

  def hasObject(self, id):
    """
    Check if the portal has an id.
    """
    return id in self.objectIds()

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getPortalObject')
  def getPortalObject(self):
    return self

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getPortalType')
  def getPortalType(self):
    return self.portal_type

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getTitle')
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
    return getattr(self, 'uid', 0)

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getParentUid')
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
  security.declareProtected(Permissions.ModifyPortalContent, 'setLastId')
  def setLastId(self, id):
    self.last_id = id

  security.declareProtected(Permissions.AccessContentsInformation, 'getUrl')
  def getUrl(self, REQUEST=None):
    """
      Returns the absolute path of an object
    """
    return join(self.getPhysicalPath(),'/')

  # Old name - for compatibility
  security.declareProtected(Permissions.AccessContentsInformation, 'getPath')
  getPath = getUrl

  security.declareProtected(Permissions.AccessContentsInformation, 'searchFolder')
  def searchFolder(self, **kw):
    """
      Search the content of a folder by calling
      the portal_catalog.
    """
    if not kw.has_key('parent_uid'):
      kw['parent_uid'] = self.uid
    return self.portal_catalog.searchResults(**kw)

  security.declareProtected(Permissions.AccessContentsInformation, 'countFolder')
  def countFolder(self, **kw):
    """
      Count the content of a folder by calling
      the portal_catalog.
    """
    if not kw.has_key('parent_uid'):
      kw['parent_uid'] = self.uid
    return self.portal_catalog.countResults(**kw)

  # Proxy methods for security reasons
  def getOwnerInfo(self):
    return self.owner_info()

  security.declarePublic('getOrderedGlobalActionList')
  def getOrderedGlobalActionList(self, action_list):
    """
    Returns a dictionnary of actions, sorted by type of object

    This should absolutely be rewritten by using clean
    concepts to separate worklists XXX
    """
    sorted_workflow_actions = {}
    sorted_global_actions = []
    other_global_actions = []
    for action in action_list:
      action['disabled'] = 0
      workflow_title = action.get('workflow_title', None)
      if workflow_title is not None:
        if not sorted_workflow_actions.has_key(workflow_title):
          sorted_workflow_actions[workflow_title] = [
            {'title':workflow_title,
             'disabled':1,
             'workflow_id':action['workflow_id']
             }
            ]
        sorted_workflow_actions[workflow_title].append(action)
      else:
        other_global_actions.append(action)
    for key in sorted(sorted_workflow_actions):
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

  # Portal methods are based on the concept of having portal-specific
  # parameters for customization. In the past, we used global parameters,
  # but it was not very good because it was very difficult
  # to customize the settings for each portal site.
  def _getPortalConfiguration(self, id):
    """
    Get a portal-specific configuration.

    Current implementation is using properties in a portal object.
    If not found, try to get a default value for backward compatibility.

    This implementation can be improved by gathering information
    from appropriate places, such as portal_types, portal_categories
    and portal_workflow.
    """
    if self.hasProperty(id):
      return self.getProperty(id)

    # Fall back to the default.
    return getattr(ERP5Defaults, id, None)

  def _getPortalGroupedTypeList(self, group):
    """
    Return a list of portal types classified to a specific group.
    The result is sorted by language (using the user language
    as default)
    """
    def getTypeList(group):
      type_list = []
      for pt in self.portal_types.objectValues():
        if group in getattr(pt, 'group_list', ()):
          type_list.append(pt.getId())

      def sortByTranslation(a, b):
        return cmp(localizer_tool.translate('ui', a),
                   localizer_tool.translate('ui', b))

      type_list.sort(sortByTranslation)
      return tuple(type_list)

    localizer_tool = getToolByName(self, 'Localizer')
    language = localizer_tool.get_selected_language()
    # language should be cached in Transaction Cache if performance issue

    getTypeList = CachingMethod(getTypeList,
                                id=(('_getPortalGroupedTypeList', language), group),
                                cache_factory='erp5_content_medium')

    return getTypeList(group) # Although this method is called get*List, it
                              # returns a tuple - renaming to be considered

  def _getPortalGroupedCategoryList(self, group):
    """
    Return a list of base categories classified to a specific group.
    """
    def getCategoryList(group):
      category_list = []
      for bc in self.portal_categories.objectValues():
        if group in bc.getCategoryTypeList():
          category_list.append(bc.getId())
      return tuple(category_list)

    getCategoryList = CachingMethod(
                            getCategoryList,
                            id=('_getPortalGroupedCategoryList', group),
                            cache_factory='erp5_content_medium')
    return getCategoryList(group)

  def _getPortalGroupedStateList(self, group):
    """
    Return a list of workflow states classified to a specific group.
    """
    def getStateList(group):
      state_dict = {}
      for wf in self.portal_workflow.objectValues():
        if getattr(wf, 'states', None):
          for state in wf.states.objectValues():
            if group in getattr(state, 'type_list', ()):
              state_dict[state.getId()] = None
      return tuple(state_dict.keys())

    getStateList = CachingMethod(getStateList,
                                 id=('_getPortalGroupedStateList', group),
                                 cache_factory='erp5_content_medium')
    return getStateList(group)

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getPortalDefaultSectionCategory')
  def getPortalDefaultSectionCategory(self):
    """
    Return a default section category. This method is deprecated.
    """
    LOG('ERP5Site', 0, 'getPortalDefaultSectionCategory is deprecated;'+
        ' use portal_preferences.getPreferredSectionCategory instead.')
    section_category = self.portal_preferences.getPreferredSectionCategory()

    # XXX This is only for backward-compatibility.
    if not section_category:
      section_category = self._getPortalConfiguration(
                                'portal_default_section_category')

    return section_category

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getPortalResourceTypeList')
  def getPortalResourceTypeList(self):
    """
      Return resource types.
    """
    return self._getPortalGroupedTypeList('resource') or \
           self._getPortalConfiguration('portal_resource_type_list')

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getPortalSubVariationTypeList')
  def getPortalSubVariationTypeList(self):
    """
      Return resource types.
    """
    return self._getPortalGroupedTypeList('sub_variation')

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getPortalSubVariationBaseCategoryList')
  def getPortalSubVariationBaseCategoryList(self):
    """
      Return variation base categories.
    """
    return self._getPortalGroupedCategoryList('sub_variation')

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getPortalVariationTypeList')
  def getPortalVariationTypeList(self):
    """
      Return variation types.
    """
    return self._getPortalGroupedTypeList('variation') or \
           self._getPortalConfiguration('portal_variation_type_list')

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getPortalNodeTypeList')
  def getPortalNodeTypeList(self):
    """
      Return node types.
    """
    return self._getPortalGroupedTypeList('node') or \
           self._getPortalConfiguration('portal_node_type_list')

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getPortalPaymentNodeTypeList')
  def getPortalPaymentNodeTypeList(self):
    """
      Return payment node types.
    """
    return self._getPortalGroupedTypeList('payment_node') or \
           self._getPortalConfiguration('portal_payment_node_type_list')

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getPortalInvoiceTypeList')
  def getPortalInvoiceTypeList(self):
    """
      Return invoice types.
    """
    return self._getPortalGroupedTypeList('invoice') or \
           self._getPortalConfiguration('portal_invoice_type_list')

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getPortalOrderTypeList')
  def getPortalOrderTypeList(self):
    """
      Return order types.
    """
    return self._getPortalGroupedTypeList('order') or \
           self._getPortalConfiguration('portal_order_type_list')

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getPortalDeliveryTypeList')
  def getPortalDeliveryTypeList(self):
    """
      Return delivery types.
    """
    return self._getPortalGroupedTypeList('delivery') or \
           self._getPortalConfiguration('portal_delivery_type_list')

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getPortalTransformationTypeList')
  def getPortalTransformationTypeList(self):
    """
      Return transformation types.
    """
    return self._getPortalGroupedTypeList('transformation') or \
           self._getPortalConfiguration('portal_transformation_type_list')

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getPortalVariationBaseCategoryList')
  def getPortalVariationBaseCategoryList(self):
    """
      Return variation base categories.
    """
    return self._getPortalGroupedCategoryList('variation') or \
           self._getPortalConfiguration('portal_variation_base_category_list')

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getPortalOptionBaseCategoryList')
  def getPortalOptionBaseCategoryList(self):
    """
      Return option base categories.
    """
    return self._getPortalGroupedCategoryList('option') or \
           self._getPortalConfiguration('portal_option_base_category_list')

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getPortalInvoiceMovementTypeList')
  def getPortalInvoiceMovementTypeList(self):
    """
      Return invoice movement types.
    """
    return self._getPortalGroupedTypeList('invoice_movement') or \
           self._getPortalConfiguration('portal_invoice_movement_type_list')

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getPortalTaxMovementTypeList')
  def getPortalTaxMovementTypeList(self):
    """
      Return tax movement types.
    """
    return self._getPortalGroupedTypeList('tax_movement') or \
           self._getPortalConfiguration('portal_tax_movement_type_list')


  security.declareProtected(Permissions.AccessContentsInformation,
                            'getPortalOrderMovementTypeList')
  def getPortalOrderMovementTypeList(self):
    """
      Return order movement types.
    """
    return self._getPortalGroupedTypeList('order_movement') or \
           self._getPortalConfiguration('portal_order_movement_type_list')

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getPortalDeliveryMovementTypeList')
  def getPortalDeliveryMovementTypeList(self):
    """
      Return delivery movement types.
    """
    return self._getPortalGroupedTypeList('delivery_movement') or \
           self._getPortalConfiguration('portal_delivery_movement_type_list')

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getPortalSupplyTypeList')
  def getPortalSupplyTypeList(self):
    """
      Return supply types.
    """
    return self._getPortalGroupedTypeList('supply') or \
           self._getPortalConfiguration('portal_supply_type_list')

  security.declareProtected(Permissions.AccessContentsInformation,
                              'getPortalRuleTypeList')
  def getPortalRuleTypeList(self):
    """
      Return rule types.
    """
    return self._getPortalGroupedTypeList('rule')

  security.declareProtected(Permissions.AccessContentsInformation,
                              'getPortalProjectTypeList')
  def getPortalProjectTypeList(self):
    """
      Return project types.
    """
    return self._getPortalGroupedTypeList('project')

  security.declareProtected(Permissions.AccessContentsInformation,
                              'getPortalDocumentTypeList')
  def getPortalDocumentTypeList(self):
    """
      Return document types.
    """
    return self._getPortalGroupedTypeList('document')

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getPortalWebDocumentTypeList')
  def getPortalWebDocumentTypeList(self):
    """
      Return web page types.
    """
    return self._getPortalGroupedTypeList('web_document')

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getPortalFileDocumentTypeList')
  def getPortalFileDocumentTypeList(self):
    """
      Return file document types.
    """
    return self._getPortalGroupedTypeList('file_document')

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getPortalRecentDocumentTypeList')
  def getPortalRecentDocumentTypeList(self):
    """
      Return recent document types.
    """
    return self._getPortalGroupedTypeList('recent_document')

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getPortalTemplateDocumentTypeList')
  def getPortalTemplateDocumentTypeList(self):
    """
      Return template document types.
    """
    return self._getPortalGroupedTypeList('template_document')

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getPortalMyDocumentTypeList')
  def getPortalMyDocumentTypeList(self):
    """
      Return my document types.
    """
    return self._getPortalGroupedTypeList('my_document')

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getPortalCrawlerIndexTypeList')
  def getPortalCrawlerIndexTypeList(self):
    """
      Return crawler index types.
    """
    return self._getPortalGroupedTypeList('crawler_index')

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getPortalBudgetVariationTypeList')
  def getPortalBudgetVariationTypeList(self):
    """
      Return budget variation types.
    """
    return self._getPortalGroupedTypeList('budget_variation')

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getPortalSupplyPathTypeList')
  def getPortalSupplyPathTypeList(self):
    """
      Return supply path types.
    """
    return self._getPortalGroupedTypeList('supply_path') or \
           self._getPortalConfiguration('portal_supply_path_type_list')

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getPortalBusinessProcessTypeList')
  def getPortalBusinessProcessTypeList(self):
    """
      Return business process types.
    """
    return self._getPortalGroupedTypeList('business_process') or \
           self._getPortalConfiguration('portal_business_process_type_list')

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getPortalBusinessStateTypeList')
  def getPortalBusinessStateTypeList(self):
    """
      Return business state types.
    """
    return self._getPortalGroupedTypeList('business_state') or \
           self._getPortalConfiguration('portal_business_state_type_list')

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getPortalBusinessPathTypeList')
  def getPortalBusinessPathTypeList(self):
    """
      Return business path types.
    """
    return self._getPortalGroupedTypeList('business_path') or \
           self._getPortalConfiguration('portal_business_path_type_list')

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getPortalAcquisitionMovementTypeList')
  def getPortalAcquisitionMovementTypeList(self):
    """
      Return acquisition movement types.
    """
    return tuple(list(self.getPortalOrderMovementTypeList()) +
                 list(self.getPortalDeliveryMovementTypeList()) +
                 list(self.getPortalTaxMovementTypeList()) +
                 list(self.getPortalInvoiceMovementTypeList()))

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getPortalMovementTypeList')
  def getPortalMovementTypeList(self):
    """
      Return movement types.
    """
    return tuple(list(self.getPortalOrderMovementTypeList()) +
                 list(self.getPortalDeliveryMovementTypeList()) +
                 list(self.getPortalInvoiceMovementTypeList()) +
                 list(self.getPortalTaxMovementTypeList()) +
                 ['Simulation Movement'])

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getPortalSimulatedMovementTypeList')
  def getPortalSimulatedMovementTypeList(self):
    """
      Return simulated movement types.
    """
    return tuple([x for x in self.getPortalMovementTypeList() \
                  if x not in self.getPortalContainerTypeList()])

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getPortalContainerTypeList')
  def getPortalContainerTypeList(self):
    """
      Return container types.
    """
    return self._getPortalGroupedTypeList('container') or \
           self._getPortalConfiguration('portal_container_type_list')

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getPortalContainerLineTypeList')
  def getPortalContainerLineTypeList(self):
    """
      Return container line types.
    """
    return self._getPortalGroupedTypeList('container_line') or \
           self._getPortalConfiguration('portal_container_line_type_list')

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getPortalItemTypeList')
  def getPortalItemTypeList(self):
    """
      Return item types.
    """
    return self._getPortalGroupedTypeList('item') or \
           self._getPortalConfiguration('portal_item_type_list')

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getPortalDiscountTypeList')
  def getPortalDiscountTypeList(self):
    """
      Return discount types.
    """
    return self._getPortalGroupedTypeList('discount') or \
           self._getPortalConfiguration('portal_discount_type_list')

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getPortalProductTypeList')
  def getPortalProductTypeList(self):
    """
      Return physical goods types.
    """
    return self._getPortalGroupedTypeList('product') or \
           self._getPortalConfiguration('portal_product_type_list')

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getPortalServiceTypeList')
  def getPortalServiceTypeList(self):
    """
      Return immaterial services types.
    """
    return self._getPortalGroupedTypeList('service') or \
           self._getPortalConfiguration('portal_service_type_list')

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getPortalAlarmTypeList')
  def getPortalAlarmTypeList(self):
    """
      Return alarm types.
    """
    return self._getPortalGroupedTypeList('alarm') or \
           self._getPortalConfiguration('portal_alarm_type_list')

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getPortalPaymentConditionTypeList')
  def getPortalPaymentConditionTypeList(self):
    """
      Return payment condition types.
    """
    return self._getPortalGroupedTypeList('payment_condition') or \
           self._getPortalConfiguration('portal_payment_condition_type_list')

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getPortalBalanceTransactionLineTypeList')
  def getPortalBalanceTransactionLineTypeList(self):
    """
      Return balance transaction line types.
    """
    return self._getPortalGroupedTypeList('balance_transaction_line') or \
           self._getPortalConfiguration(
                  'portal_balance_transaction_line_type_list')

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getPortalCurrentInventoryStateList')
  def getPortalCurrentInventoryStateList(self):
    """
      Return current inventory states.
    """
    return self._getPortalGroupedStateList('current_inventory') or \
           self._getPortalConfiguration('portal_current_inventory_state_list')

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getPortalTransitInventoryStateList')
  def getPortalTransitInventoryStateList(self):
    """
      Return transit inventory states.
    """
    return self._getPortalGroupedStateList('transit_inventory') or \
           self._getPortalConfiguration('portal_transit_inventory_state_list')

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getPortalDraftOrderStateList')
  def getPortalDraftOrderStateList(self):
    """
      Return draft order states.
    """
    return self._getPortalGroupedStateList('draft_order') or \
           self._getPortalConfiguration('portal_draft_order_state_list')

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getPortalPlannedOrderStateList')
  def getPortalPlannedOrderStateList(self):
    """
      Return planned order states.
    """
    return self._getPortalGroupedStateList('planned_order') or \
           self._getPortalConfiguration('portal_planned_order_state_list')

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getPortalReservedInventoryStateList')
  def getPortalReservedInventoryStateList(self):
    """
      Return reserved inventory states.
    """
    return self._getPortalGroupedStateList('reserved_inventory') or \
        self._getPortalConfiguration('portal_reserved_inventory_state_list')

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getPortalFutureInventoryStateList')
  def getPortalFutureInventoryStateList(self):
    """
      Return future inventory states.
    """
    return self._getPortalGroupedStateList('future_inventory') or \
           self._getPortalConfiguration('portal_future_inventory_state_list')

  security.declareProtected(Permissions.AccessContentsInformation,
                          'getPortalUpdatableAmortisationTransactionStateList')
  def getPortalUpdatableAmortisationTransactionStateList(self):
    """
      Return states when Amortisation Transaction can be updated
      by amortisation_transaction_builder.
    """
    return self._getPortalConfiguration(
        'portal_updatable_amortisation_transaction_state_list')

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getPortalGroupedSimulationStateList')
  def getPortalGroupedSimulationStateList(self):
    """
      Return all states which is related to simulation state workflow and state type
    """
    def getStateList():
      state_dict = {}
      for wf in self.portal_workflow.objectValues():
        if getattr(wf, 'variables', None) and \
           wf.variables.getStateVar() == 'simulation_state':
          if getattr(wf, 'states', None):
            for state in wf.states.objectValues():
              if getattr(state, 'type_list', None):
                state_dict[state.getId()] = None
      return tuple(sorted(state_dict.keys()))

    getStateList = CachingMethod(getStateList,
                                 id=('getPortalGroupedSimulationStateList'),
                                 cache_factory='erp5_content_medium')
    return getStateList()

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getPortalColumnBaseCategoryList')
  def getPortalColumnBaseCategoryList(self):
    """
      Return column base categories.
    """
    return self._getPortalGroupedCategoryList('column') or \
           self._getPortalConfiguration('portal_column_base_category_list')

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getPortalLineBaseCategoryList')
  def getPortalLineBaseCategoryList(self):
    """
      Return line base categories.
    """
    return self._getPortalGroupedCategoryList('line') or \
           self._getPortalConfiguration('portal_line_base_category_list')

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getPortalTabBaseCategoryList')
  def getPortalTabBaseCategoryList(self):
    """
      Return tab base categories.
    """
    return self._getPortalGroupedCategoryList('tab') or \
           self._getPortalConfiguration('portal_tab_base_category_list')

  def getPortalDefaultGapRoot(self):
    """
      Return the Accounting Plan to use by default (return the root node)
    """
    LOG('ERP5Site', 0,
        'getPortalDefaultGapRoot is deprecated; ' \
        'use portal_preferences.getPreferredAccountingTransactionGap instead.')

    return self.portal_preferences.getPreferredAccountingTransactionGap() or \
           self._getPortalConfiguration('portal_default_gap_root')

  def getPortalAccountingMovementTypeList(self) :
    """
      Return accounting movement type list.
    """
    return self._getPortalGroupedTypeList('accounting_movement') or \
        self._getPortalConfiguration('portal_accounting_movement_type_list')

  def getPortalAccountingTransactionTypeList(self) :
    """
      Return accounting transaction movement type list.
    """
    return self._getPortalGroupedTypeList('accounting_transaction') or \
      self._getPortalConfiguration('portal_accounting_transaction_type_list')

  def getPortalAssignmentBaseCategoryList(self):
    """
      Return List of category values to generate security groups.
    """
    return self._getPortalGroupedCategoryList('assignment') or \
        self._getPortalConfiguration('portal_assignment_base_category_list')

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getPortalTicketTypeList')
  def getPortalTicketTypeList(self):
    """
    Return ticket types.
    """
    return self._getPortalGroupedTypeList('ticket')

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getPortalEventTypeList')
  def getPortalEventTypeList(self):
    """
    Return event types.
    """
    return self._getPortalGroupedTypeList('event')

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getPortalDivergenceTesterTypeList')
  def getPortalDivergenceTesterTypeList(self):
    """
    Return divergence tester types.
    """
    return self._getPortalGroupedTypeList('divergence_tester')

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getPortalCalendarPeriodTypeList')
  def getPortalCalendarPeriodTypeList(self):
    """
    Return calendar period types.
    """
    return self._getPortalGroupedTypeList('calendar_period')

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getPortalModuleTypeList')
  def getPortalModuleTypeList(self):
    """
    Return module types.
    """
    return self._getPortalGroupedTypeList('module')

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getPortalInventoryMovementTypeList')
  def getPortalInventoryMovementTypeList(self):
    """
    Return inventory movement types.
    """
    return self._getPortalGroupedTypeList('inventory_movement')

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getPortalMovementGroupTypeList')
  def getPortalMovementGroupTypeList(self):
    """
    Return movement group types.
    """
    return self._getPortalGroupedTypeList('movement_group')

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getDefaultModuleId')
  def getDefaultModuleId(self, portal_type, default=MARKER):
    """
    Return default module id where a object with portal_type can
    be created.
    """
    portal_object = self
    module_id = None
    # first try to find by naming convention
    expected_module_id = portal_type.lower().replace(' ','_')
    if portal_object._getOb(expected_module_id, None) is not None:
      module_id = expected_module_id
    else:
      expected_module_id += '_module'
      if portal_object._getOb(expected_module_id, None) is not None:
        module_id = expected_module_id
      # then look for module where the type is allowed
      else:
        for expected_module_id in portal_object.objectIds(spec=('ERP5 Folder',)):
          module = portal_object._getOb(expected_module_id, None)
          if module is not None:
            if portal_type in self.portal_types[module.getPortalType()].\
                                      allowed_content_types:
              module_id = expected_module_id
              break

    if module_id is None:
      if default is not MARKER:
        return default
      else:
        # now we fail
        LOG('ERP5Site, getDefaultModuleId', 0,
            'Unable to find default module for portal_type: %s' % \
             portal_type)
        raise ValueError, 'Unable to find module for portal_type: %s' % \
               portal_type

    return module_id

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getDefaultModule')
  def getDefaultModule(self, portal_type, default=MARKER):
    """
      Return default module where a object with portal_type can be created
    """
    module_id = self.getDefaultModuleId(portal_type, default)
    if module_id:
      return getattr(self, module_id, None)
    return None

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

    if kw is not None:
      new_instance._edit(force_update=1, **kw)
    if immediate_reindex:
      new_instance.immediateReindexObject()
    return new_instance

  security.declarePublic('getVisibleAllowedContentTypeList')
  def getVisibleAllowedContentTypeList(self):
    """Users cannot add anything in an ERP5Site using standard interface.
    """
    return ()

  def log(self, description, content='', level=INFO):
    """Put a log message """
    warnings.warn("The usage of ERP5Site.log is deprecated.\n"
                  "Please use Products.ERP5Type.Log.log instead.",
                  DeprecationWarning)
    unrestrictedLog(description, content = content, level = level)

  security.declarePublic('setPlacelessDefaultReindexParameters')
  def setPlacelessDefaultReindexParameters(self, **kw):
    # This method sets the default keyword parameters to reindex. This is useful
    # when you need to specify special parameters implicitly (e.g. to reindexObject).
    # Those parameters will affect all reindex calls, not just ones on self.
    tv = getTransactionalVariable(self)
    key = ('default_reindex_parameter', )
    tv[key] = kw

  security.declarePublic('setPlacelessDefaultActivateParameters')
  def setPlacelessDefaultActivateParameters(self, **kw):
    # This method sets the default keyword parameters to activate. This is useful
    # when you need to specify special parameters implicitly (e.g. to reindexObject).
    # Those parameters will affect all activate calls, not just ones on self.
    tv = getTransactionalVariable(self)
    key = ('default_activate_parameter', )
    tv[key] = kw

  security.declarePublic('getPlacelessDefaultReindexParameters')
  def getPlacelessDefaultReindexParameters(self):
    # This method returns default reindex parameters to self.
    # The result can be either a dict object or None.
    tv = getTransactionalVariable(self)
    key = ('default_reindex_parameter', )
    return tv.get(key)

  security.declarePublic('getPlacelessDefaultActivateParameters')
  def getPlacelessDefaultActivateParameters(self):
    # This method returns default activate parameters to self.
    # The result can be either a dict object or None.
    tv = getTransactionalVariable(self)
    key = ('default_activate_parameter', )
    return tv.get(key)

Globals.InitializeClass(ERP5Site)

def getBootstrapDirectory():
  """
    Return the name of the bootstrap directory
  """
  product_path = package_home(globals())
  return os.path.join(product_path, 'bootstrap')

class ERP5Generator(PortalGenerator):

  klass = ERP5Site

  def getBootstrapDirectory(self):
    return getBootstrapDirectory()

  def create(self,
             parent,
             id,
             create_userfolder,
             erp5_catalog_storage,
             erp5_sql_connection_type,
             erp5_sql_connection_string,
             erp5_sql_deferred_connection_type,
             cmf_activity_sql_connection_type,
             cmf_activity_sql_connection_string,
             create_activities=1,
             reindex=1,
             **kw):
    id = str(id)
    portal = self.klass(id=id)
    # Make sure reindex will not be called until business templates
    # will be installed
    setattr(portal, 'isIndexable', 0)
    parent._setObject(id, portal)
    # Return the fully wrapped object.
    p = parent.this()._getOb(id)

    erp5_sql_deferred_connection_string = erp5_sql_connection_string
    p._setProperty('erp5_catalog_storage',
                   erp5_catalog_storage, 'string')
    p._setProperty('erp5_sql_connection_type',
                   erp5_sql_connection_type, 'string')
    p._setProperty('erp5_sql_connection_string',
                   erp5_sql_connection_string, 'string')
    p._setProperty('erp5_sql_deferred_connection_type',
                   erp5_sql_deferred_connection_type, 'string')
    p._setProperty('erp5_sql_deferred_connection_string',
                   erp5_sql_deferred_connection_string, 'string')
    p._setProperty('cmf_activity_sql_connection_type',
                   cmf_activity_sql_connection_type, 'string')
    p._setProperty('cmf_activity_sql_connection_string',
                   cmf_activity_sql_connection_string, 'string')
    # XXX hardcoded charset
    p._setProperty('management_page_charset', 'UTF-8', 'string')
    self.setup(p, create_userfolder, create_activities=create_activities,
        reindex=reindex, **kw)
    return p

  def setupLastTools(self, p, **kw):
    """
    Set up finals tools
    We want to set the activity tool only at the end to
    make sure that we do not put un the queue the full reindexation
    """
    # Add Activity Tool
    if kw.has_key('create_activities') and int(kw['create_activities'])==1:
      if not p.hasObject('portal_activities'):
        addTool = p.manage_addProduct['CMFActivity'].manage_addTool
        addTool('CMF Activity Tool', None) # Allow user to select active/passive
      # Initialize Activities
      portal_activities = getToolByName(p, 'portal_activities', None)
      if portal_activities is not None:
        if kw.get('update', 0):
          keep = 1
        else:
          keep = 0
        portal_activities.manageClearActivities(keep=keep)

  def setupTemplateTool(self, p, **kw):
    """
    Setup the Template Tool. Security must be set strictly.
    """
    addTool = p.manage_addProduct['ERP5'].manage_addTool
    addTool('ERP5 Template Tool', None)
    context = p.portal_templates
    permission_list = context.possible_permissions()
    for permission in permission_list:
      context.manage_permission(permission, ['Manager'], 0)

  def setupTools(self, p,**kw):
    """
    Set up initial tools.
    """
    if not 'portal_actions' in p.objectIds():
      PortalGenerator.setupTools(self, p)
      p._delObject('portal_types')

    # It is better to remove portal_catalog
    # which is ZCatalog as soon as possible,
    # because the API is not the completely same as ERP5Catalog,
    # and ZCatalog is useless for ERP5 after all.
    update = kw.get('update', 0)
    portal_catalog = getToolByName(p, 'portal_catalog', None)
    if portal_catalog is not None and \
       portal_catalog.meta_type != 'ZSQLCatalog' and \
       not update:
      p._delObject('portal_catalog')

    # Add CMF Report Tool
    if not p.hasObject('portal_report'):
      try:
        addTool = p.manage_addProduct['CMFReportTool'].manage_addTool
        addTool('CMF Report Tool', None)
      except AttributeError:
        pass

    # Add ERP5 Tools
    addTool = p.manage_addProduct['ERP5'].manage_addTool
    if not p.hasObject('portal_categories'):
      addTool('ERP5 Categories', None)
    if not p.hasObject('portal_rules'):
      addTool('ERP5 Rule Tool', None)
    if not p.hasObject('portal_ids'):
      addTool('ERP5 Id Tool', None)
    if not p.hasObject('portal_simulation'):
      addTool('ERP5 Simulation Tool', None)
    if not p.hasObject('portal_templates'):
      self.setupTemplateTool(p)
    if not p.hasObject('portal_trash'):
      addTool('ERP5 Trash Tool', None)
    if not p.hasObject('portal_alarms'):
      addTool('ERP5 Alarm Tool', None)
    if not p.hasObject('portal_domains'):
      addTool('ERP5 Domain Tool', None)
    if not p.hasObject('portal_deliveries'):
      addTool('ERP5 Delivery Tool', None)
    if not p.hasObject('portal_orders'):
      addTool('ERP5 Order Tool', None)
    if not p.hasObject('portal_tests'):
      addTool('ERP5 Test Tool', None)
    if not p.hasObject('portal_password'):
      addTool('ERP5 Password Tool', None)
    if not p.hasObject('portal_acknowledgements'):
      addTool('ERP5 Acknowledgement Tool', None)

    # Add ERP5Type Tool
    addTool = p.manage_addProduct['ERP5Type'].manage_addTool
    if not p.hasObject('portal_caches'):
      addTool('ERP5 Cache Tool', None)
    if not p.hasObject('portal_memcached'):
      addTool('ERP5 Memcached Tool', None)
    if not p.hasObject('portal_types'):
      addTool('ERP5 Types Tool', None)
      transaction.get().beforeCommitHook(lambda:
        p.portal_types.Base_setDefaultSecurity())

    try:
      addTool = p.manage_addProduct['ERP5Subversion'].manage_addTool
      if not p.hasObject('portal_subversion'):
        addTool('ERP5 Subversion Tool', None)
    except AttributeError:
      pass

    # Add ERP5Type Tools
    addTool = p.manage_addProduct['ERP5Type'].manage_addTool
    if not p.hasObject('portal_classes'):
      if allowClassTool():
        addTool('ERP5 Class Tool', None)
      else:
        addTool('ERP5 Dummy Class Tool', None)

    # Add ERP5 SQL Catalog Tool
    addTool = p.manage_addProduct['ERP5Catalog'].manage_addTool
    if not p.hasObject('portal_catalog'):
      addTool('ERP5 Catalog', None)

    # Add Default SQL connection
    if p.erp5_sql_connection_type == 'Z MySQL Database Connection':
      if not p.hasObject('erp5_sql_connection'):
        addSQLConnection = p.manage_addProduct['ZMySQLDA'].\
                                     manage_addZMySQLConnection
        addSQLConnection('erp5_sql_connection',
                         'ERP5 SQL Server Connection',
                         p.erp5_sql_connection_string)
    elif p.erp5_sql_connection_type == 'Z Gadfly':
      pass

    # Add Deferred SQL Connections
    if p.erp5_sql_deferred_connection_type == \
        'Z MySQL Deferred Database Connection':
      if not p.hasObject('erp5_sql_deferred_connection'):
        addSQLConnection = p.manage_addProduct['ZMySQLDDA'].\
            manage_addZMySQLDeferredConnection
        addSQLConnection('erp5_sql_deferred_connection',
                         'ERP5 SQL Server Deferred Connection',
                         p.erp5_sql_deferred_connection_string)
    elif p.erp5_sql_deferred_connection_type == 'Z Gadfly':
      pass

    # Add Activity SQL Connections
    if p.cmf_activity_sql_connection_type == 'Z MySQL Database Connection':
      if not p.hasObject('cmf_activity_sql_connection'):
        addSQLConnection = p.manage_addProduct['ZMySQLDA'].\
                                     manage_addZMySQLConnection
        addSQLConnection('cmf_activity_sql_connection',
                         'CMF Activity SQL Server Connection',
                         p.cmf_activity_sql_connection_string)
      # Warning : This transactionless connection is created with
      # the activity connection string and not the catalog's because
      # it's not compatible with the hot reindexing feature.
      # Though, it has nothing to do with activities.
      # The only difference compared to activity connection is the
      # minus prepended to the connection string.
      if not p.hasObject('erp5_sql_transactionless_connection'):
        addSQLConnection = p.manage_addProduct['ZMySQLDA'].\
                                     manage_addZMySQLConnection
        addSQLConnection('erp5_sql_transactionless_connection',
                         'ERP5 Transactionless SQL Server Connection',
                         '-%s' % p.cmf_activity_sql_connection_string)
    elif p.cmf_activity_sql_connection_type == 'Z Gadfly':
      pass

    # Add ERP5Form Tools
    addTool = p.manage_addProduct['ERP5Form'].manage_addTool
    if not p.hasObject('portal_selections'):
      addTool('ERP5 Selections', None)
    if not p.hasObject('portal_preferences'):
      addTool('ERP5 Preference Tool', None)

    try:
      # Add ERP5SyncML Tools
      addTool = p.manage_addProduct['ERP5SyncML'].manage_addTool
      if not p.hasObject('portal_synchronizations'):
        addTool('ERP5 Synchronizations', None)
    except AttributeError:
      pass

    # Add Message Catalog
    if not 'Localizer' in p.objectIds():
      addLocalizer = p.manage_addProduct['Localizer'].manage_addLocalizer
      addLocalizer('', ('en',))
    localizer = getToolByName(p, 'Localizer')
    addMessageCatalog = localizer.manage_addProduct['Localizer']\
                                      .manage_addMessageCatalog
    if 'erp5_ui' not in localizer.objectIds():
      if 'default' in localizer.objectIds():
        localizer.manage_delObjects('default')
      addMessageCatalog('default', 'ERP5 Localized Messages', ('en',))
      addMessageCatalog('erp5_ui', 'ERP5 Localized Interface', ('en',))
      addMessageCatalog('erp5_content', 'ERP5 Localized Content', ('en',))

    # Add an error_log
    if 'error_log' not in p.objectIds():
      manage_addErrorLog(p)
      p.error_log.setProperties(keep_entries=20,
                                copy_to_zlog=True,
                                ignored_exceptions=('NotFound', 'Redirect'))


    # Remove unused default actions
    def removeActionsFromTool(tool, remove_list):
      action_id_list = [i.id for i in tool.listActions()]
      remove_index_list = []
      for i in remove_list:
        if i in action_id_list:
          remove_index_list.append(action_id_list.index(i))
      if remove_index_list:
        tool.deleteActions(remove_index_list)
    # membership tool
    removeActionsFromTool(p.portal_membership,
                          ('addFavorite', 'mystuff', 'favorites', 'logged_in',
                           'manage_members'))
    # actions tool
    removeActionsFromTool(p.portal_actions, ('folderContents',))
    # properties tool
    removeActionsFromTool(p.portal_properties, ('configPortal',))
    # remove unused action providers
    for i in ('portal_registration', 'portal_discussion', 'portal_syndication'):
      p.portal_actions.deleteActionProvider(i)

  def setupMembersFolder(self, p):
    """
    ERP5 is not a CMS
    """
    pass

  def setupDefaultSkins(self, p):
    from Products.CMFCore.DirectoryView import addDirectoryViews
    from Products.CMFDefault  import cmfdefault_globals
    from Products.CMFActivity import cmfactivity_globals
    ps = getToolByName(p, 'portal_skins')
    addDirectoryViews(ps, 'skins', cmfdefault_globals)
    addDirectoryViews(ps, 'skins', cmfactivity_globals)
    ps.manage_addProduct['OFSP'].manage_addFolder(id='external_method')
    ps.manage_addProduct['OFSP'].manage_addFolder(id='custom')
    # Set the 'custom' layer a high priority, so it remains the first
    #   layer when installing new business templates.
    ps['custom'].manage_addProperty("business_template_skin_layer_priority", 100.0, "float")
    skin_folder_list = [ 'custom'
                       , 'external_method'
                       , 'activity'
                       , 'zpt_content'
                       , 'zpt_generic'
                       , 'zpt_control'
                       , 'content'
                       , 'generic'
                       , 'control'
                       , 'Images'
                       ]
    skin_folders = ', '.join(skin_folder_list)
    ps.addSkinSelection( 'View'
                       , skin_folders
                       , make_default = 1
                       )
    ps.addSkinSelection( 'Print'
                       , skin_folders
                       , make_default = 0
                       )
    ps.addSkinSelection( 'CSV'
                       , skin_folders
                       , make_default = 0
                       )
    p.setupCurrentSkin()

  def setupWorkflow(self, p):
    """
    Set up workflows for business templates
    """
    tool = getToolByName(p, 'portal_workflow', None)
    if tool is None:
      return
    for wf_id in ('business_template_building_workflow',
                  'business_template_installation_workflow'):
      if wf_id in tool.objectIds():
        tool.manage_delObjects([wf_id])
    bootstrap_dir = self.getBootstrapDirectory()
    business_template_building_workflow = os.path.join(
                                 bootstrap_dir,
                                 'business_template_building_workflow.xml')
    tool._importObjectFromFile(business_template_building_workflow)
    business_template_installation_workflow = os.path.join(
                                 bootstrap_dir,
                                 'business_template_installation_workflow.xml')
    tool._importObjectFromFile(business_template_installation_workflow)
    tool.setChainForPortalTypes( ( 'Business Template', ),
                                 ( 'business_template_building_workflow',
                                   'business_template_installation_workflow' ) )

  def setupIndex(self, p, **kw):
    # Make sure all tools and folders have been indexed
    if not kw.get('reindex', 1):
      return
    skins_tool = getToolByName(p, 'portal_skins', None)
    if skins_tool is None:
      return
    # When no SQL connection was define on the site,
    # we don't want to make it crash
    if p.erp5_sql_connection_type is not None:
      setattr(p, 'isIndexable', 1)
      portal_catalog = p.portal_catalog
      # Clear portal ids sql table, like this we do not take
      # ids for a previously created web site
      portal_catalog.getSQLCatalog().z0_drop_portal_ids()
      # Then clear the catalog and reindex it
      portal_catalog.manage_catalogClear()
      skins_tool["erp5_core"].ERP5Site_reindexAll()

  def setupUserFolder(self, p):
    # We use if possible ERP5Security, then NuxUserGroups
    try:
      from Products import ERP5Security
      from Products import PluggableAuthService
    except ImportError:
      ERP5Security = None
      try:
        import Products.NuxUserGroups
        withnuxgroups = 1
      except ImportError:
        withnuxgroups = 0
    if ERP5Security is not None:
      # Use Pluggable Auth Service instead of the standard acl_users.
      p.manage_addProduct['PluggableAuthService'].addPluggableAuthService()
      pas_dispatcher = p.acl_users.manage_addProduct['PluggableAuthService']
      # Add legacy ZODB support
      pas_dispatcher.addZODBUserManager('zodb_users')
      pas_dispatcher.addZODBGroupManager('zodb_groups')
      pas_dispatcher.addZODBRoleManager('zodb_roles')
      # Add CMF Portal Roles
      #XXX Maybe it will be no longer required once PAS is the standard
      p.acl_users.zodb_roles.addRole('Member')
      p.acl_users.zodb_roles.addRole('Reviewer')
      # Register ZODB Interface
      p.acl_users.zodb_users.manage_activateInterfaces(
                                       ('IAuthenticationPlugin',
                                        'IUserEnumerationPlugin',
                                        'IUserAdderPlugin'))
      p.acl_users.zodb_groups.manage_activateInterfaces(
                                       ('IGroupsPlugin',
                                       'IGroupEnumerationPlugin'))
      p.acl_users.zodb_roles.manage_activateInterfaces(
                                       ('IRoleEnumerationPlugin',
                                        'IRolesPlugin',
                                        'IRoleAssignerPlugin'))
      # Add ERP5UserManager
      erp5security_dispatcher = p.acl_users.manage_addProduct['ERP5Security']
      erp5security_dispatcher.addERP5UserManager('erp5_users')
      erp5security_dispatcher.addERP5GroupManager('erp5_groups')
      erp5security_dispatcher.addERP5RoleManager('erp5_roles')
      erp5security_dispatcher.addERP5UserFactory('erp5_user_factory')
      # Register ERP5UserManager Interface
      p.acl_users.erp5_users.manage_activateInterfaces(
                                        ('IAuthenticationPlugin',
                                        'IUserEnumerationPlugin',))
      p.acl_users.erp5_groups.manage_activateInterfaces(('IGroupsPlugin',))
      p.acl_users.erp5_roles.manage_activateInterfaces(('IRolesPlugin',))
      p.acl_users.erp5_user_factory.manage_activateInterfaces(
                                        ('IUserFactoryPlugin',))
    elif withnuxgroups:
      # NuxUserGroups user folder
      p.manage_addProduct['NuxUserGroups'].addUserFolderWithGroups()
    else:
      # Standard user folder
      PortalGenerator.setupUserFolder(self, p)

  def setupPermissions(self, p):
    permission_dict = {
      'Access Transient Objects'     : ('Manager', 'Anonymous'),
      'Access contents information'  : ('Manager', 'Member', 'Anonymous'),
      'Access future portal content' : ('Manager', 'Reviewer'),
      'Access session data'          : ('Manager', 'Anonymous'),
      'AccessContentsInformation'    : ('Manager', 'Member'),
      'Change local roles'           : ('Manager', ),
      'Add portal content'           : ('Manager', 'Owner'),
      'Add portal folders'           : ('Manager', 'Owner'),
      'Delete objects'               : ('Manager', 'Owner'),
      'FTP access'                   : ('Manager', 'Owner'),
      'List folder contents'         : ('Manager', 'Member'),
      'List portal members'          : ('Manager', 'Member'),
      'List undoable changes'        : ('Manager', ),
      'Manage properties'            : ('Manager', 'Owner'),
      'Modify portal content'        : ('Manager', 'Owner'),
      'Reply to item'                : ('Manager', 'Member'),
      'Review portal content'        : ('Manager', 'Reviewer'),
      'Search ZCatalog'              : ('Manager', 'Member'),
      'Set own password'             : ('Manager', ),
      'Set own properties'           : ('Manager', 'Member'),
      'Use mailhost services'        : ('Manager', 'Member'),
      'Undo changes'                 : ('Manager', 'Owner'),
      'View'                         : ('Manager', 'Member',
                                        'Owner', 'Anonymous'),
      'View management screens'      : ('Manager', 'Owner')
    }

    for permission in p.ac_inherited_permissions(1):
      name = permission[0]
      role_list = permission_dict.get(name, ('Manager',))
      p.manage_permission(name, roles=role_list, acquire=0)

  def setup(self, p, create_userfolder, **kw):
    update = kw.get('update', 0)

    if getattr(p, 'setDefaultSorting', None) is not None:
      p.setDefaultSorting('id', 0)

    self.setupTools(p, **kw)

    if not p.hasObject('MailHost'):
      self.setupMailHost(p)

    if create_userfolder and not p.hasObject('acl_users'):
      self.setupUserFolder(p)

    if not p.hasObject('cookie_authentication'):
      self.setupCookieAuth(p)

    if 'Member' not in getattr(p, '__ac_roles__', ()):
      self.setupRoles(p)
    if not update:
      self.setupPermissions(p)
      self.setupDefaultSkins(p)

    # Finish setup
    if not p.hasObject('Members'):
      self.setupMembersFolder(p)

    # ERP5 Design Choice is that all content should be user defined
    # Content is disseminated through business templates
    self.setupPortalTypes(p)

    if not p.hasObject('content_type_registry'):
      self.setupMimetypes(p)
    if not update:
      self.setupWorkflow(p)

    if not update:
      self.setupERP5Core(p,**kw)

    # Make sure the cache is initialized
    p.portal_caches.updateCache()

    self.setupLastTools(p, **kw)

    # Make sure tools are cleanly indexed with a uid before creating children
    # XXX for some strange reason, member was indexed 5 times
    if not update:
      self.setupIndex(p, **kw)

  def setupPortalTypes(self, p):
    """
    Install the portal_type of Business Template
    """
    tool = getToolByName(p, 'portal_types', None)
    if tool is None:
      return
    for t in BusinessTemplate,:
      t = t.factory_type_information
      if not tool.hasObject(t['id']):
        tool._setObject(t['id'],
          ERP5TypeInformation(portal_type=ERP5TypeInformation.portal_type,
                              uid=None, **t))

  def setupERP5Core(self,p,**kw):
    """
    Install the core part of ERP5
    """
    template_tool = getToolByName(p, 'portal_templates', None)
    if template_tool is None:
      return
    if template_tool.getInstalledBusinessTemplate('erp5_core') is None:
      bootstrap_dir = self.getBootstrapDirectory()
      # XXX erp5_type BT will be merged into erp5_core later.
      for bt in 'erp5_core', 'erp5_type', p.erp5_catalog_storage, 'erp5_xhtml_style':
        if not bt:
          continue
        template = os.path.join(bootstrap_dir, bt)
        if not os.path.exists(template):
          template = os.path.join(bootstrap_dir, '%s.bt5' % bt)

        id = template_tool.generateNewId()
        template_tool.download(template, id=id)
        template_tool[id].install(**kw)
