# -*- coding: utf-8 -*-
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

from six.moves import map
import threading
from weakref import ref as weakref
from OFS.Application import Application, AppInitializer
from Products.ERP5Type import Globals
from Products.ERP5Type.Globals import package_home

from Products.SiteErrorLog.SiteErrorLog import manage_addErrorLog
from ZPublisher import BeforeTraverse
from ZPublisher.BaseRequest import RequestContainer
from AccessControl import ClassSecurityInfo
from Products.CMFDefault.Portal import CMFSite
from Products.ERP5Type import Permissions
from Products.ERP5Type.Core.Folder import FolderMixIn
from Acquisition import aq_base
from Products.ERP5Type.Accessor.Constant import PropertyGetter as ConstantGetter
from Products.ERP5Type.Cache import caching_instance_method
from Products.ERP5Type.Cache import CachingMethod, CacheCookieMixin
from Products.ERP5Type.ERP5Type import ERP5TypeInformation
from Products.ERP5Type.Log import log as unrestrictedLog
from Products.CMFActivity.Errors import ActivityPendingError
import ERP5Defaults
from Products.ERP5Type.TransactionalVariable import getTransactionalVariable
from Products.ERP5Type.dynamic.portal_type_class import synchronizeDynamicModules

from zLOG import LOG, INFO, WARNING, ERROR
from string import join
import os
import warnings
import transaction
from App.config import getConfiguration
MARKER = []


# Site Creation DTML
manage_addERP5SiteFormDtml = Globals.HTMLFile('dtml/addERP5Site', globals())

def manage_addERP5SiteForm(*args, **kw):
  """
    Make getCatalogStorageList available from inside the dtml.
  """
  kw['getCatalogStorageList'] = getCatalogStorageList
  return manage_addERP5SiteFormDtml(*args, **kw)

default_sql_connection_string = 'test test'

# ERP5Site Constructor
def manage_addERP5Site(self,
                       id,
                       title='ERP5',
                       description='',
                       create_userfolder=1,
                       create_activities=True,
                       email_from_address='postmaster@localhost',
                       email_from_name='Portal Administrator',
                       validate_email=0,
                       erp5_catalog_storage='erp5_mysql_innodb_catalog',
                       erp5_sql_connection_string=default_sql_connection_string,
                       cmf_activity_sql_connection_string=default_sql_connection_string,
                       bt5_repository_url='',
                       bt5='',
                       id_store_interval='',
                       cloudooo_url='',
                       light_install=0,
                       reindex=1,
                       sql_reset=0,
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
                 erp5_sql_connection_string,
                 cmf_activity_sql_connection_string,
                 bt5_repository_url,
                 bt5,
                 id_store_interval,
                 cloudooo_url,
                 create_activities=create_activities,
                 light_install=light_install,
                 reindex=reindex,
                 sql_reset=sql_reset)
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

def addERP5Tool(portal, id, portal_type):
  if portal.hasObject(id):
    return
  import erp5.portal_type
  klass = getattr(erp5.portal_type, portal_type)
  obj = klass()
  portal._setObject(id, obj)

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


class _site(threading.local):
  """Class for getting and setting the site in the thread global namespace
  """
  site = ()

  def __new__(cls):
    self = threading.local.__new__(cls)
    return self.__get, self.__set

  def __get(self, REQUEST=None):
    """Returns the currently processed site, optionally wrapped in a request
    """
    while True:
      app, site_id = self.site[-1]
      app = app()
      if app._p_jar.opened:
        if REQUEST is None:
          return getattr(app, site_id)
        return getattr(app.__of__(RequestContainer(REQUEST=REQUEST)), site_id)
      del self.site[-1]

  def __set(self, site):
    app = aq_base(site.aq_parent)
    self.site = [x for x in self.site if x[0]() is not app]
    # Use weak references for automatic cleanup. In practice, this is probably
    # useless, because there is no reason a thread reopen the database.
    self.site.append((weakref(app, self.__del), site.id))

  def __del(self, app):
    self.site = [x for x in self.site if x[0] is not app]

getSite, setSite = _site()


class ERP5Site(FolderMixIn, CMFSite, CacheCookieMixin):
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
  # Default value, prevents error during upgrade
  isIndexable = ConstantGetter('isIndexable', value=True)
  # There can remain a lot a activities to be processed once all BT5 are
  # installed, and scalability tests want a reliable way to know when the site
  # is ready to be tortured.
  isPortalBeingCreated = ConstantGetter('isPortalBeingCreated', value=False)

  _properties = (
      { 'id':'title',
        'type':'string'},
      { 'id':'description',
        'type':'text'},
      # setProperty cannot be used for this property as it is a property
      # pointing to _version_priority_list and valid_property_id doesn't
      # accept property name starting with '_'. The property getter always
      # returns at least erp5 version.
      #
      # Also, it must not be a local property as it is stored in ZODB and
      # would not be displayed 'Properties' tab with old sites, thus could not
      # be edited.
      { 'id': 'version_priority_list',
        'type': 'lines' }
      )
  title = ''
  description = ''

  # Declarative security
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  security.declarePublic('isSubtreeIndexable')
  def isSubtreeIndexable(self):
    """
    Allow a container to preempt indexability of its content, without having
    to set "isIndexable = False" on (at minimum) its immediate children.

    The meaning of calling this method on an instance where
    isAncestryIndexable returns False is undefined.
    """
    return self.isIndexable

  def __before_publishing_traverse__(self, self2, request):
    request.RESPONSE.realm = None
    return super(ERP5Site, self).__before_publishing_traverse__(self2, request)

  def _initSystemPreference(self, cloudooo_url):
    """
    Post-addERP5Site code to make sure that cloudoo is configured,
    which is often required by the configurator.
    """
    preference_tool = self.portal_preferences
    id = 'default_system_preference'
    portal_type = 'System Preference'
    for pref in preference_tool.objectValues(portal_type=portal_type):
      if pref.getPreferenceState() == 'global':
        break
    else:
      from Products.ERP5Form.PreferenceTool import Priority
      pref = preference_tool.newContent(id, portal_type,
        priority=Priority.SITE, title='Default ' + portal_type)
      pref.enable()
    cloudooo_url = cloudooo_url.split(',')
    pref.setPreferredDocumentConversionServerUrlList(cloudooo_url)

  def _createInitialSiteManager(self):
    # This section of code is inspired by
    # Products.CMFDefault.upgrade.to21.upgrade_root_site_manager(),
    # specificallythe 'except ComponentLookupError:' clause, and also
    # by Products.CMFDefault.PortalObjectBase.__init__
    from zope.component.globalregistry import base
    from five.localsitemanager import (PersistentComponents,
                                       find_next_sitemanager)
    next = find_next_sitemanager(self)
    if next is None:
      next = base
    name = '++etc++site'
    sm = PersistentComponents(name, (next,))
    sm.__parent__ = aq_base(self)
    self.setSiteManager(sm)
    LOG('ERP5Site', 0, "Site manager '%s' added." % name)

  def _doTranslationDomainRegistration(self):
    from zope.i18n.interfaces import ITranslationDomain
    from Products.Localizer.MessageCatalog import (
      message_catalog_alias_sources
    )
    sm = self._components
    for message_catalog in self.Localizer.objectValues():
      sm.registerUtility(message_catalog,
                         provided=ITranslationDomain,
                         name=message_catalog.getId())
      for alias in message_catalog_alias_sources.get(message_catalog.getId()):
        sm.registerUtility(message_catalog,
                           provided=ITranslationDomain,
                           name=alias)

  def _registerMissingTools(self):
    from Products.CMFCore import interfaces, utils
    tool_id_list = ("portal_skins", "portal_types", "portal_membership",
                    "portal_url", "portal_workflow")
    if None in map(self.get, tool_id_list):
      return False
    sm = self._components
    for tool_id in tool_id_list:
      tool = self[tool_id]
      tool_interface = utils._tool_interface_registry.get(tool_id)
      if tool_interface is not None:
        # Note: already registered tools will be either:
        # - updated
        # - registered again after being unregistered
        sm.registerUtility(aq_base(tool), tool_interface)
    return True

  # backward compatibility auto-migration
  def getSiteManager(self):
    # NOTE: do not add a docstring! This method is private by virtue of
    # not having it.

    # XXX-Leo: Consider moving this method and all methods that it calls
    # into a monkeypatch of an optional product. This product could have
    # its own tests for migration without actually cluttering the original
    # source code and would only need to be installed in sites needing
    # migration from Zope 2.8

    # This code is an alteration of
    # OFS.ObjectManager.ObjectManager.getSiteManager(), and is exactly
    # as cheap as it is on the case that self._components is already
    # set.
    _components = self._components
    if _components is None:
      # only create _components
      self._createInitialSiteManager()
      _components = self._components
      # Now that we have a sitemanager, se can do things that require
      # one. Including setting up ZTK style utilities and adapters. We
      # can even call setSite(self), as long as we roll back that later,
      # since we are actually in the middle of a setSite() call.
      from zope.site.hooks import getSite, setSite
      old_site = getSite()
      try:
        setSite(self)
        self._doTranslationDomainRegistration()
        self._registerMissingTools()
      finally:
        setSite(old_site)
    else:
      self._registerMissingTools()
    return _components

  security.declareProtected(Permissions.View, 'view')
  def view(self):
    """
      Returns the default view.
      Implemented for consistency
    """
    return self.index_html()

  def __of__(self, parent):
    self = CMFSite.__of__(self, parent)
    # Use a transactional variable for performance reason,
    # since ERP5Site.__of__ is called quite often.
    tv = getTransactionalVariable()
    # Check 'parent' is the root because some objects like '_components'
    # store the site in '__parent__'.
    if 'ERP5Site.__of__' not in tv and type(parent) is Application:
      tv['ERP5Site.__of__'] = None
      setSite(self)

      try:
        component_tool = self.portal_components
      except AttributeError:
        # This should only happen before erp5_core is installed
        synchronizeDynamicModules(self)
      else:
        if not component_tool.reset():
          # Portal Types may have been reset even if Components haven't
          # (change of Interaction Workflow...)
          synchronizeDynamicModules(self)

    return self

  security.declareProtected(Permissions.AccessContentsInformation,
                            'isDeletable')
  def isDeletable(self, check_relation):
    return False

  security.declarePrivate('manage_beforeDelete')
  def manage_beforeDelete(self, item, container):
    # skin is setup during __before_publishing_traverse__, which
    # doesn't happen when the object is being deleted from the management
    # interface, but we need it to be set for portal_activities when we're
    # being deleted.
    self.setupCurrentSkin(self.REQUEST)
    return ERP5Site.inheritedAttribute('manage_beforeDelete')(self,
                                                              item,
                                                              container)

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
        portal_activities = self.portal_activities
      except AttributeError:
        pass
      else:
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

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getVersionPriorityList')
  def getVersionPriorityList(self):
    """
    Return the Component version priorities defined on the site in descending
    order. Whatever happens, erp5 version must always be returned otherwise it
    may render the site unusable when all Products will have been migrated
    """
    return getattr(self, '_version_priority_list', None) or ('erp5 | 0.0',)

  security.declareProtected(Permissions.ModifyPortalContent,
                            'setVersionPriorityList' )
  def setVersionPriorityList(self, version_priority_tuple):
    """
    Set Version Priority List and make sure that erp5 version is always
    defined whatever the given value is

    XXX-arnau: must be written through an interaction workflow when ERP5Site
               will become a real ERP5 object...
    """
    if not isinstance(version_priority_tuple, tuple):
      version_priority_tuple = tuple(version_priority_tuple)

    # erp5 version must always be present, thus add it at the end if it's not
    # already there
    for version_priority in version_priority_tuple:
      if version_priority.split('|')[0].strip() == 'erp5':
        break
    else:
      version_priority_tuple = version_priority_tuple + ('erp5 | 0.0',)

    self._version_priority_list = version_priority_tuple

    # Reset cached value of getVersionPriorityNameList() if present
    try:
      del self._v_version_priority_name_list
    except AttributeError:
      pass

    # Make sure that reset is not performed when creating a new site
    if not getattr(self, '_v_bootstrapping', False):
      try:
        self.portal_components.resetOnceAtTransactionBoundary()
      except AttributeError:
        # This should only happen before erp5_core is installed
        pass

  version_priority_list = property(getVersionPriorityList,
                                   setVersionPriorityList)

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getVersionPriorityNameList')
  def getVersionPriorityNameList(self):
    """
    Get only the version names ordered by priority and cache it as it is used
    very often in Component import hooks
    """
    if getattr(self, '_v_version_priority_name_list', None) is None:
      self._v_version_priority_name_list = \
          [name.split('|')[0].strip() for name in self.getVersionPriorityList()]

    return self._v_version_priority_name_list

  # Make sure ERP5Site follow same API as Products.ERP5Type.Base

  # _getProperty is missing, but since there are no protected properties
  # on an ERP5 Site, we can just use getProperty instead.
  _getProperty = CMFSite.getProperty

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

  security.declareProtected(Permissions.AccessContentsInformation, 'getRelativeUrl')
  def getRelativeUrl(self):
    """
      Returns the url of an object relative to the portal site.
    """
    return self.getPortalObject().portal_url.getRelativeUrl(self)

  # Old name - for compatibility
  security.declareProtected(Permissions.AccessContentsInformation, 'getPath')
  getPath = getUrl

  security.declareProtected(Permissions.AccessContentsInformation, 'opaqueValues')
  def opaqueValues(self, *args, **kw):
    # XXX nonsense of inheriting from CMFSite that calls __before_traversal__
    # and tries to load subobjects of the portal too early
    return []

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

  security.declareProtected(Permissions.ManagePortal, 'getPromiseParameter')
  def getPromiseParameter(self, section, option):
    """
    Read external promise parameters.

    The parameters should be provided by an external configuration file.
    Location of this configuration file is defined in the zope configuration
    file in a product_config named as the path of the ERP5 site.
    Example if the site id is erp5:
      <product-config /erp5>
        promise_path /tmp/promise.cfg
      </product-config>

    The promise configuration is a simple ConfigParser readable file (a list of
    section containing a list of string parameters.

    getPromiseParameter returns None if the parameter isn't found.
    """
    config = getConfiguration()
    if getattr(config, 'product_config', None) is not None:
      parameter_dict = config.product_config.get(self.getPath(), {})
      if 'promise_path' in parameter_dict:
        promise_path = parameter_dict['promise_path']
        import ConfigParser
        configuration = ConfigParser.ConfigParser()
        configuration.read(promise_path)
        try:
          return configuration.get(section, option)
        except (ConfigParser.NoOptionError, ConfigParser.NoSectionError):
          pass
    return None

  def _getPortalGroupedTypeList(self, group, enable_sort=True):
    """
    Return a list of portal types classified to a specific group.
    The result is sorted by language (using the user language
    as default)

    Enable_sort parameter was added in order to allows looking groups
    of portal type without sorting. This is better for performance
    """
    def getTypeList(group):
      type_list = []
      for pt in self.portal_types.listTypeInfo():
        if group in getattr(pt, 'group_list', ()):
          type_list.append(pt.getId())

      if enable_sort and len(type_list) >= 2:
        # XXX (Seb), this code must be moved in another place.
        # It is inefficient to always sort here for some particular
        # needs of the user interface
        translate = localizer_tool.translate
        type_list.sort(key=lambda x:translate('ui', x))
      return tuple(type_list)

    if enable_sort:
      # language should be cached in Transaction Cache if performance issue
      localizer_tool = self.Localizer
      language = localizer_tool.get_selected_language()
    else:
      localizer_tool = language = None

    getTypeList = CachingMethod(getTypeList,
                                id=(('_getPortalGroupedTypeList', language), group,
                                    enable_sort),
                                cache_factory='erp5_content_medium',
                                )

    return getTypeList(group) # Although this method is called get*List, it
                              # returns a tuple - renaming to be considered

  @caching_instance_method(id='ERP5Site._getPortalGroupedTypeSet',
     cache_factory='erp5_content_long')
  def _getPortalGroupedTypeSet(self, group):
    """
    Same as _getPortalGroupedTypeList, but returns a set, better for
    performance when looking for matching portal types
    """
    return set(self._getPortalGroupedTypeList(group, enable_sort=False))

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
                            'getPortalOpenOrderTypeList')
  def getPortalOpenOrderTypeList(self):
    """
      Return open order types.
    """
    return self._getPortalGroupedTypeList('open_order') or \
           self._getPortalConfiguration('portal_open_order_type_list')

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
                            'getPortalModelPathTypeList')
  def getPortalModelPathTypeList(self):
    """
      Return model_path types.
    """
    return self._getPortalGroupedTypeList('model_path') or \
           self._getPortalConfiguration('portal_model_path_type_list')

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
                              'getPortalConstraintTypeList')
  def getPortalConstraintTypeList(self):
    """
      Return constraint types.
    """
    return self._getPortalGroupedTypeList('constraint')

  security.declareProtected(Permissions.AccessContentsInformation,
                              'getPortalPropertyTypeList')
  def getPortalPropertyTypeList(self):
    """
      Return property types.
    """
    return self._getPortalGroupedTypeList('property')

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
                              'getPortalEmbeddedDocumentTypeList')
  def getPortalEmbeddedDocumentTypeList(self):
    """
      Return embedded document types.
    """
    return self._getPortalGroupedTypeList('embedded_document')

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
                            'getPortalAcquisitionMovementTypeList')
  def getPortalAcquisitionMovementTypeList(self):
    """
      Return acquisition movement types.
    """
    r = list(self.getPortalOrderMovementTypeList())
    r += self.getPortalDeliveryMovementTypeList()
    r += self.getPortalTaxMovementTypeList()
    r += self.getPortalInvoiceMovementTypeList()
    return tuple(r)

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getPortalMovementTypeList')
  def getPortalMovementTypeList(self):
    """
      Return movement types.
    """
    r = list(self.getPortalOrderMovementTypeList())
    r += self.getPortalDeliveryMovementTypeList()
    r += self.getPortalInvoiceMovementTypeList()
    r += self.getPortalTaxMovementTypeList()
    r += self.getPortalAccountingMovementTypeList()
    r.append('Simulation Movement')
    return tuple(r)

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getPortalSimulatedMovementTypeList')
  def getPortalSimulatedMovementTypeList(self):
    """
      Return simulated movement types.
    """
    r = set(self.getPortalMovementTypeList())
    r.difference_update(self.getPortalContainerTypeList())
    return tuple(r)

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
                            'getPortalSaleTypeList')
  def getPortalSaleTypeList(self):
    """
    Return sale types.
    """
    return self._getPortalGroupedTypeList('sale')

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getPortalPurchaseTypeList')
  def getPortalPurchaseTypeList(self):
    """
    Return purchase types.
    """
    return self._getPortalGroupedTypeList('purchase')

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getPortalInternalTypeList')
  def getPortalInternalTypeList(self):
    """
    Return internal types.
    """
    return self._getPortalGroupedTypeList('internal')

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
                            'getPortalDomainTypeList')
  def getPortalDomainTypeList(self):
    """
      Return domain types.
    """
    return self._getPortalGroupedTypeList('domain')

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

  def getPortalSecurityCategoryMapping(self):
    """
      Returns a list of pairs composed of a script id and a list of base
      category ids to use for computing security groups.

      This is used during indexation, so involved scripts must not rely on
      catalog at any point in their execution.

      Example:
        (
          ('script_1', ['base_category_1', 'base_category_2', ...]),
          ('script_2', ['base_category_1', 'base_category_3', ...])
        )
    """
    return getattr(
      self,
      'ERP5Type_getSecurityCategoryMapping',
      lambda: ( # BBB
        (
          'ERP5Type_getSecurityCategoryFromAssignment',
          self.getPortalAssignmentBaseCategoryList(),
        ),
      ),
    )()

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
                            'getPortalInterfacePostTypeList')
  def getPortalInterfacePostTypeList(self):
    """
    Return interface_post types.
    """
    return self._getPortalGroupedTypeList('interface_post')

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getPortalDivergenceTesterTypeList')
  def getPortalDivergenceTesterTypeList(self):
    """
    Return divergence tester types.
    """
    return self._getPortalGroupedTypeList('divergence_tester')

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getPortalTargetSolverTypeList')
  def getPortalTargetSolverTypeList(self):
    """
    Return target solver types.
    """
    return self._getPortalGroupedTypeList('target_solver')

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getPortalTargetSolverTypeList')
  def getPortalDeliverySolverTypeList(self):
    """
    Return delivery solver types.
    """
    return self._getPortalGroupedTypeList('delivery_solver')

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getPortalAmountGeneratorTypeList')
  def getPortalAmountGeneratorTypeList(self):
    """
    Return amount generator types.
    """
    return self._getPortalGroupedTypeList('amount_generator')

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getPortalAmountGeneratorLineTypeList')
  def getPortalAmountGeneratorLineTypeList(self):
    """
    Return amount generator line types.
    """
    return self._getPortalGroupedTypeList('amount_generator_line')

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getPortalAmountGeneratorCellTypeList')
  def getPortalAmountGeneratorCellTypeList(self):
    """
    Return amount generator cell types.
    """
    return self._getPortalGroupedTypeList('amount_generator_cell')

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getPortalAmountGeneratorAllTypeList')
  def getPortalAmountGeneratorAllTypeList(self, transformation):
    """
    Return amount generator types, including lines & cells,
    but only or without those related to transformations.
    """
    result = list(self.getPortalAmountGeneratorTypeList())
    result += self.getPortalAmountGeneratorLineTypeList()
    result += self.getPortalAmountGeneratorCellTypeList()
    if transformation:
      return tuple(x for x in result if x.startswith('Transformation'))
    return tuple(x for x in result if not x.startswith('Transformation'))

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getPortalBusinessProcessTypeList')
  def getPortalBusinessProcessTypeList(self):
    """
    Return amount generator types.
    """
    return self._getPortalGroupedTypeList('business_process')


  security.declareProtected(Permissions.AccessContentsInformation,
                            'getPortalBusinessLinkTypeList')
  def getPortalBusinessLinkTypeList(self):
    """
      Return business link types.
    """
    return self._getPortalGroupedTypeList('business_link')

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getPortalTradeModelPathTypeList')
  def getPortalTradeModelPathTypeList(self):
    """
      Return trade model path types.
    """
    return self._getPortalGroupedTypeList('trade_model_path')

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getPortalCalendarTypeList')
  def getPortalCalendarTypeList(self):
    """
    Return calendar types.
    """
    return self._getPortalGroupedTypeList('calendar')

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
                            'getPortalPersonalItemTypeList')
  def getPortalPersonalItemTypeList(self) :
    """
      Return personal item types.
    """
    return self._getPortalGroupedTypeList('personal_item')

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getPortalInventoryMovementTypeList')
  def getPortalInventoryMovementTypeList(self):
    """
    Return inventory movement types.
    """
    return self._getPortalGroupedTypeList('inventory_movement')

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getPortalInventoryTypeList')
  def getPortalInventoryTypeList(self):
    """
    Return inventory types.
    """
    return self._getPortalGroupedTypeList('inventory')

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getPortalMovementGroupTypeList')
  def getPortalMovementGroupTypeList(self):
    """
    Return movement group types.
    """
    return self._getPortalGroupedTypeList('movement_group')

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getPortalEntityTypeList')
  def getPortalEntityTypeList(self):
    """
    Returns Entity types.
    """
    return self._getPortalGroupedTypeList('entity') or\
           self._getPortalConfiguration('portal_entity_type_list')

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getPortalLoginTypeList')
  def getPortalLoginTypeList(self):
    """
    Returns Login types.
    """
    return self._getPortalGroupedTypeList('login')

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getPortalDataDescriptorTypeList')
  def getPortalDataDescriptorTypeList(self):
    """
    Returns Data Descriptor types.
    """
    return self._getPortalGroupedTypeList('data_descriptor') or\
           self._getPortalConfiguration('portal_data_descriptor_type_list')

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getPortalDataSinkTypeList')
  def getPortalDataSinkTypeList(self):
    """
    Returns Data Sink types.    
    """
    return self._getPortalGroupedTypeList('data_sink') or\
           self._getPortalConfiguration('portal_data_sink_type_list')

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getPortalDeviceTypeList')
  def getPortalDeviceTypeList(self):
    """
    Returns Device types.
    """
    return self._getPortalGroupedTypeList('device') or\
           self._getPortalConfiguration('portal_device_type_list')

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getPortalDeviceConfigurationTypeList')
  def getPortalDeviceConfigurationTypeList(self):
    """
    Returns Device Configuration types.
    """
    return self._getPortalGroupedTypeList('device_configuration') or\
           self._getPortalConfiguration('portal_device_configuration_type_list')

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getPortalPaymentRequestTypeList')
  def getPortalPaymentRequestTypeList(self):
    """
    Returns Payment Request types.
    """
    return self._getPortalGroupedTypeList('payment_request')

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getDefaultModuleId')
  def getDefaultModuleId(self, portal_type, default=MARKER, only_visible=False):
    """
    Return default module id where a object with portal_type can
    be created.
    """
    try:
      module = self.getDefaultModuleValue(portal_type, only_visible=only_visible)
    except ValueError:
      if default is MARKER:
        raise ValueError('Unable to find module for portal_type: ' + portal_type)
      return default
    else:
      return module.getId()

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getDefaultModuleValue')
  def getDefaultModuleValue(self, portal_type, default=MARKER, only_visible=False):
    """
    Return default module where a object with portal_type can be created
    portal_type (str)
      Module or top-level document portal type.
    default (anything)
      Value to return if no module can be found from given portal type.
      If not given and module is not found, ValueError is raised.
    only_visible (bool)
      When true, check that given portal type is part of module's visible
      content types, else return default.
    """
    # first try to find by naming convention
    expected_module_id = portal_type.lower().replace(' ','_')
    module = self._getOb(expected_module_id, None)
    if module is not None:
      return module
    if only_visible:
      allowed = lambda x: (
        x is not None and
        portal_type in x.getVisibleAllowedContentTypeList()
      )
    else:
      getTypeInfo = self.portal_types.getTypeInfo
      allowed = lambda x: (
        x is not None and
        portal_type in getTypeInfo(x).getTypeAllowedContentTypeList()
      )
    expected_module_id += '_module'
    module = self._getOb(expected_module_id, None)
    if allowed(module):
      return module
    # then look for module where the type is allowed
    for expected_module_id in self.objectIds(('ERP5 Folder',)):
      module = self._getOb(expected_module_id, None)
      if allowed(module):
        return module
    if default is MARKER:
      raise ValueError('Unable to find module for portal_type: ' + portal_type)
    return default

  # BBB
  security.declareProtected(
    Permissions.AccessContentsInformation,
    'getDefaultModule',
  )
  def getDefaultModule(self, portal_type, default=MARKER):
    """
    For backward-compatibility.
    Use getDefaultModuleValue (beware of slight "default" semantic change !).
    """
    module_id = self.getDefaultModuleId(portal_type, default)
    if module_id:
      return getattr(self, module_id, None)

  security.declareProtected(Permissions.AddPortalContent, 'newContent')
  def newContent(self, id=None, portal_type=None, **kw):
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

    if kw:
      new_instance._edit(force_update=1, **kw)
    return new_instance

  security.declarePublic('getVisibleAllowedContentTypeList')
  def getVisibleAllowedContentTypeList(self):
    """Users cannot add anything in an ERP5Site using standard interface.
    """
    return ()

  def log(self, *args, **kw):
    """Put a log message

    See the warning in Products.ERP5Type.Log.log
    Catchall parameters also make this method not publishable to avoid DoS.
    """
    warnings.warn("The usage of ERP5Site.log is deprecated.\n"
                  "Please use Products.ERP5Type.Log.log instead.",
                  DeprecationWarning)
    unrestrictedLog(*args, **kw)

  security.declarePublic('setPlacelessDefaultReindexParameters')
  def setPlacelessDefaultReindexParameters(self, **kw):
    # This method sets the default keyword parameters to reindex. This is useful
    # when you need to specify special parameters implicitly (e.g. to reindexObject).
    # Those parameters will affect all reindex calls, not just ones on self.
    tv = getTransactionalVariable()
    key = ('default_reindex_parameter', )
    tv[key] = kw

  security.declarePublic('getPlacelessDefaultReindexParameters')
  def getPlacelessDefaultReindexParameters(self):
    # This method returns default reindex parameters to self.
    # The result can be either a dict object or None.
    tv = getTransactionalVariable()
    key = ('default_reindex_parameter', )
    return tv.get(key)

  security.declareProtected(Permissions.ManagePortal,
                            'migrateToPortalTypeClass')
  def migrateToPortalTypeClass(self):
    # PickleUpdater() will load objects from ZODB, but any objects created
    # before must have been committed (otherwise POSKeyError is raised)
    transaction.savepoint(optimistic=True)

    from Products.ERP5Type.dynamic.persistent_migration import PickleUpdater
    from Products.ERP5Type.Tool.BaseTool import BaseTool
    PickleUpdater(self)
    for tool in self.objectValues():
      if isinstance(tool, BaseTool):
        tool_id = tool.id
        if tool_id not in ('portal_property_sheets', 'portal_components'):
          if tool_id in ('portal_categories', ):
            tool = tool.activate()
          tool.migrateToPortalTypeClass(tool_id not in (
            'portal_activities', 'portal_simulation', 'portal_templates',
            'portal_trash', 'portal_catalog'))
          if tool_id in ('portal_trash', 'portal_catalog'):
            for obj in tool.objectValues():
              obj.migrateToPortalTypeClass()

Globals.InitializeClass(ERP5Site)

def getBootstrapDirectory():
  """
    Return the name of the bootstrap directory
  """
  product_path = package_home(globals())
  return os.path.join(product_path, 'bootstrap')

def getBootstrapBusinessTemplateUrl(bt_title):
  """
    Return the path to download the given bootstrap business template
  """
  path = os.path.join(getBootstrapDirectory(), bt_title)
  if not os.path.exists(path):
    path += '.bt5'
  return path

# This PortalGenerator class was copied wholesale from CMF 1.5 which is
# identical to the one on 1.6, and hasn't been used by CMF itself since even
# 1.5, as they already used CMFSetup by then (later replaced by GenericSetup).


factory_type_information = () # No original CMF portal_types installed by default

class PortalGenerator:

    klass = CMFSite

    def setupTools(self, p):
        """Set up initial tools"""

        addCMFCoreTool = p.manage_addProduct['CMFCore'].manage_addTool
        addCMFCoreTool('CMF Actions Tool', None)
        addCMFCoreTool('CMF Catalog', None)
        addCMFCoreTool('CMF Member Data Tool', None)
        addCMFCoreTool('CMF Skins Tool', None)
        addCMFCoreTool('CMF Undo Tool', None)
        addCMFCoreTool('CMF URL Tool', None)
        addCMFCoreTool('CMF Workflow Tool', None)

        addCMFDefaultTool = p.manage_addProduct['CMFDefault'].manage_addTool
        addCMFDefaultTool('Default Discussion Tool', None)
        addCMFDefaultTool('Default Membership Tool', None)
        addCMFDefaultTool('Default Registration Tool', None)
        addCMFDefaultTool('Default Properties Tool', None)
        addCMFDefaultTool('Default Metadata Tool', None)
        addCMFDefaultTool('Default Syndication Tool', None)

        # try to install CMFUid without raising exceptions if not available
        try:
            addCMFUidTool = p.manage_addProduct['CMFUid'].manage_addTool
        except AttributeError:
            pass
        else:
            addCMFUidTool('Unique Id Annotation Tool', None)
            addCMFUidTool('Unique Id Generator Tool', None)
            addCMFUidTool('Unique Id Handler Tool', None)

    def setupMailHost(self, p):
        p.manage_addProduct['MailHost'].manage_addMailHost(
            'MailHost', smtp_host='localhost')

    def setupUserFolder(self, p):
        p.manage_addProduct['OFSP'].manage_addUserFolder()

    def setupCookieAuth(self, p):
        p.manage_addProduct['CMFCore'].manage_addCC(
            id='cookie_authentication')

    def setupRoles(self, p):
        # Set up the suggested roles.
        p.__ac_roles__ = ('Member', 'Reviewer',)

    def setupMimetypes(self, p):
        p.manage_addProduct[ 'CMFCore' ].manage_addRegistry()
        reg = p.content_type_registry

        reg.addPredicate( 'link', 'extension' )
        reg.getPredicate( 'link' ).edit( extensions="url, link" )
        reg.assignTypeName( 'link', 'Link' )

        reg.addPredicate( 'news', 'extension' )
        reg.getPredicate( 'news' ).edit( extensions="news" )
        reg.assignTypeName( 'news', 'News Item' )

        reg.addPredicate( 'document', 'major_minor' )
        reg.getPredicate( 'document' ).edit( major="text", minor="" )
        reg.assignTypeName( 'document', 'Document' )

        reg.addPredicate( 'image', 'major_minor' )
        reg.getPredicate( 'image' ).edit( major="image", minor="" )
        reg.assignTypeName( 'image', 'Image' )

        reg.addPredicate( 'file', 'major_minor' )
        reg.getPredicate( 'file' ).edit( major="application", minor="" )
        reg.assignTypeName( 'file', 'File' )

    def setupDefaultProperties(self, p, title, description,
                               email_from_address, email_from_name,
                               validate_email, default_charset=''):
        p._setProperty('email_from_address', email_from_address, 'string')
        p._setProperty('email_from_name', email_from_name, 'string')
        p._setProperty('validate_email', validate_email and 1 or 0, 'boolean')
        p._setProperty('default_charset', default_charset, 'string')
        p._setProperty('enable_permalink', 0, 'boolean')
        p.title = title
        p.description = description


class ERP5Generator(PortalGenerator):

  klass = ERP5Site

  def create(self,
             parent,
             id,
             create_userfolder,
             erp5_catalog_storage,
             erp5_sql_connection_string,
             cmf_activity_sql_connection_string,
             bt5_repository_url,
             bt5,
             id_store_interval,
             cloudooo_url,
             create_activities=True,
             reindex=1,
             **kw):
    id = str(id)
    portal = self.klass(id=id)
    # Make sure reindex will not be called until business templates
    # will be installed
    setattr(portal, 'isIndexable', ConstantGetter('isIndexable', value=False))

    # This is only used to refine log level.
    # Has no functional use, and should never have any:
    # if you use it for something else than a logging-oriented hint,
    # trolls *will* chase you and haunt you in your dreams
    portal._v_bootstrapping = True

    parent._setObject(id, portal)
    # Return the fully wrapped object.
    p = parent.this()._getOb(id)

    erp5_sql_deferred_connection_string = erp5_sql_connection_string
    p._setProperty('erp5_catalog_storage',
                   erp5_catalog_storage, 'string')
    p._setProperty('erp5_sql_connection_string',
                   erp5_sql_connection_string, 'string')
    p._setProperty('erp5_sql_deferred_connection_string',
                   erp5_sql_deferred_connection_string, 'string')
    p._setProperty('cmf_activity_sql_connection_string',
                   cmf_activity_sql_connection_string, 'string')
    p._setProperty('management_page_charset', 'UTF-8', 'string')
    self.setup(p, create_userfolder, create_activities=create_activities,
        reindex=reindex, **kw)

    p._v_bootstrapping = False

    reindex_all_tag = 'ERP5Site_reindexAll'
    upgrade_tag = 'updgradeSite'
    preference_tag = 'initSystemPreference'
    if bt5_repository_url:
      p.portal_templates.repository_dict = dict.fromkeys(bt5_repository_url.split())
      if bt5:
        p.portal_templates.activate(
          # XXX: Is it useful to wait for indexing ?
          after_tag=reindex_all_tag,
          tag=upgrade_tag,
        ).upgradeSite(bt5.split(), update_catalog=True)
    if id_store_interval != '':
      id_store_interval = int(id_store_interval)
      if id_store_interval < 0:
        raise TypeError('id_store_interval must be a positive integer')
      ob = p.portal_ids._getLatestGeneratorValue(
          'mysql_non_continuous_increasing')
      if id_store_interval:
        ob._setStoreInterval(id_store_interval)
      else:
        ob._setStoredInZodb(0)
    if cloudooo_url:
      p.portal_activities.activateObject(
        p,
        after_tag=(reindex_all_tag, upgrade_tag),
        tag=preference_tag,
      )._initSystemPreference(cloudooo_url=cloudooo_url)
    id_ = 'isPortalBeingCreated'
    setattr(p, id_, ConstantGetter(id_, value=True))
    p.portal_activities.activateObject(
      p,
      after_tag=(reindex_all_tag, upgrade_tag, preference_tag),
    )._delPropValue(id_)
    return p

  @classmethod
  def bootstrap(cls, context, bt_name, item_name, content_path_list):
    bt_path = getBootstrapBusinessTemplateUrl(bt_name)
    from Products.ERP5.Document.BusinessTemplate import quote
    traverse = context.unrestrictedTraverse
    top = os.path.join(bt_path, item_name, context.id)
    prefix_len = len(os.path.join(top, ''))
    for root, dirs, files in os.walk(top):
      container_path = root[prefix_len:]
      container_obj = traverse(container_path)
      load = container_obj._importObjectFromFile
      if container_path:
        id_set = {x[:-4] for x in files if x[-4:] == '.xml'}
      else:
        id_set = set()
        for content_path in content_path_list:
          try:
            traverse(content_path)
          except (KeyError, AttributeError):
            id_set.add(quote(content_path.split('/', 1)[0]))
      dirs[:] = id_set.intersection(dirs)
      for id_ in id_set:
        if not container_obj.hasObject(id_):
          load(os.path.join(root, id_ + '.xml'),
               verify=False, set_owner=False, suppress_events=True)

  @staticmethod
  def bootstrap_allow_type(types_tool, portal_type):
    from xml.etree.cElementTree import parse
    bt_path = getBootstrapBusinessTemplateUrl('erp5_core')
    types_tool[portal_type].allowed_content_types = [x.text for x in parse(
      os.path.join(bt_path, 'PortalTypeAllowedContentTypeTemplateItem', 'allowed_content_types.xml')
      ).iterfind("portal_type[@id='%s']/*" % portal_type)]

  def setupLastTools(self, p, **kw):
    """
    Set up finals tools
    We want to set the activity tool only at the end to
    make sure that we do not put un the queue the full reindexation
    """
    addERP5Tool(p, 'portal_rules', 'Rule Tool')
    addERP5Tool(p, 'portal_simulation', 'Simulation Tool')
    addERP5Tool(p, 'portal_deliveries', 'Delivery Tool')
    addERP5Tool(p, 'portal_orders', 'Order Tool')

  def setupTemplateTool(self, p, **kw):
    """
    Setup the Template Tool. Security must be set strictly.
    """
    addERP5Tool(p, 'portal_templates', 'Template Tool')
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

    # It is better to remove portal_catalog
    # which is ZCatalog as soon as possible,
    # because the API is not the completely same as ERP5Catalog,
    # and ZCatalog is useless for ERP5 after all.
    update = kw.get('update', 0)
    try:
      if p.portal_catalog.meta_type != 'ZSQLCatalog' and not update:
        p._delObject('portal_catalog')
    except AttributeError:
      pass

    # Add CMF Report Tool
    if not p.hasObject('portal_report'):
      try:
        addTool = p.manage_addProduct['CMFReportTool'].manage_addTool
        addTool('CMF Report Tool', None)
      except AttributeError:
        pass

    # Add ERP5 Tools
    addERP5Tool(p, 'portal_categories', 'Category Tool')
    addERP5Tool(p, 'portal_ids', 'Id Tool')
    if not p.hasObject('portal_templates'):
      self.setupTemplateTool(p)
    addERP5Tool(p, 'portal_trash', 'Trash Tool')
    addERP5Tool(p, 'portal_alarms', 'Alarm Tool')
    addERP5Tool(p, 'portal_domains', 'Domain Tool')
    addERP5Tool(p, 'portal_tests', 'Test Tool')
    addERP5Tool(p, 'portal_password', 'Password Tool')
    addERP5Tool(p, 'portal_introspections', 'Introspection Tool')
    addERP5Tool(p, 'portal_acknowledgements', 'Acknowledgement Tool')

    # Add ERP5Type Tool
    addERP5Tool(p, 'portal_caches', 'Cache Tool')
    addERP5Tool(p, 'portal_memcached', 'Memcached Tool')

    # Add erp5 catalog tool
    addERP5Tool(p, 'portal_catalog', 'Catalog Tool')

    sql_reset = kw.get('sql_reset', 0)
    def addSQLConnection(id, title, **kw):
      if p.hasObject(id):
        return
      # Warning : The transactionless connection is created with
      # the activity connection string and not the catalog's because
      # it's not compatible with the hot reindexing feature.
      # Though, it has nothing to do with activities.
      # The only difference compared to activity connection is the
      # minus prepended to the connection string.
      if id == 'erp5_sql_transactionless_connection':
        connection_string = '-' + p.cmf_activity_sql_connection_string
      else:
        connection_string = getattr(p, id + '_string')
      manage_add(id, title, connection_string, **kw)
      if not sql_reset and p[id]().tables():
        raise Exception("Database %r is not empty." % connection_string)

    # Add Z MySQL Connections
    manage_add = p.manage_addProduct['ZMySQLDA'].manage_addZMySQLConnection
    addSQLConnection('erp5_sql_connection',
                     'ERP5 SQL Server Connection')
    addSQLConnection('erp5_sql_deferred_connection',
                     'ERP5 SQL Server Deferred Connection',
                     deferred=True)
    addSQLConnection('erp5_sql_transactionless_connection',
                     'ERP5 Transactionless SQL Server Connection')
    # Add Activity SQL Connections
    manage_add = p.manage_addProduct['CMFActivity'].manage_addActivityConnection
    addSQLConnection('cmf_activity_sql_connection',
                     'CMF Activity SQL Server Connection')

    # Add ERP5Form Tools
    addERP5Tool(p, 'portal_selections', 'Selection Tool')
    addERP5Tool(p, 'portal_preferences', 'Preference Tool')

    # Add Message Catalog
    if not 'Localizer' in p.objectIds():
      addLocalizer = p.manage_addProduct['Localizer'].manage_addLocalizer
      addLocalizer('', ('en',))
    localizer = p.Localizer
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
      from Products.CMFCore.interfaces import IActionProvider
      if not IActionProvider.providedBy(tool):
        # On CMF 2.x, some tools (portal_membership)
        # are no longer action providers
        return
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

  # this lists only the skin layers of Products.CMFDefault we are actually
  # interested in.
  CMFDEFAULT_FOLDER_LIST = ['Images']
  def addCMFDefaultDirectoryViews(self, p):
    """Semi-manually create DirectoryViews since CMFDefault 2.X no longer
    registers the "skins" directory, only its subdirectories, making it
    unusable with Products.CMFCore.DirectoryView.addDirectoryViews."""
    from Products.CMFCore.DirectoryView import createDirectoryView, _generateKey
    import Products.CMFDefault

    ps = p.portal_skins
    # get the layer directories actually present
    for cmfdefault_skin_layer in self.CMFDEFAULT_FOLDER_LIST:
      reg_key = _generateKey(Products.CMFDefault.__name__,
                             'skins/' + cmfdefault_skin_layer)
      createDirectoryView(ps, reg_key)

  def setupDefaultSkins(self, p):
    ps = p.portal_skins
    self.addCMFDefaultDirectoryViews(p)
    ps.manage_addProduct['OFSP'].manage_addFolder(id='external_method')
    ps.manage_addProduct['OFSP'].manage_addFolder(id='custom')
    # Set the 'custom' layer a high priority, so it remains the first
    #   layer when installing new business templates.
    ps['custom'].manage_addProperty("business_template_skin_layer_priority", 100.0, "float")
    skin_folder_list = [ 'custom'
                       , 'external_method'
                       ] + self.CMFDEFAULT_FOLDER_LIST
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
    workflow_list = ['business_template_building_workflow',
                     'business_template_installation_workflow']
    tool = p.portal_workflow
    tool.manage_delObjects(filter(tool.hasObject, workflow_list))
    self.bootstrap(tool, 'erp5_core', 'WorkflowTemplateItem', workflow_list)
    tool.setChainForPortalTypes(('Business Template',), workflow_list)

  def setupIndex(self, p, **kw):
    # Make sure all tools and folders have been indexed
    if kw.get('reindex', 1):
      delattr(p, 'isIndexable')
      # Clear portal ids sql table, like this we do not take
      # ids for a previously created web site
      p.portal_ids.clearGenerator(all=True)
      # Calling ERP5Site_reindexAll is important, as some needed indexation
      # activities may have been skipped (not spawned) while portal was tagged
      # as non-indexable. Maybe not spawning these activities is a bug, in
      # which case some bootstrap tricks are needed until portal_activities
      # becomes available.
      p.ERP5Site_reindexAll(clear_catalog=True)

  def setupUserFolder(self, p):
      # Use Pluggable Auth Service instead of the standard acl_users.
      p.manage_addProduct['PluggableAuthService'].addPluggableAuthService()
      pas_dispatcher = p.acl_users.manage_addProduct['PluggableAuthService']
      # Add legacy ZODB support
      pas_dispatcher.addZODBUserManager('zodb_users')
      pas_dispatcher.addZODBGroupManager('zodb_groups')
      pas_dispatcher.addZODBRoleManager('zodb_roles')
      # Add CMF Portal Roles
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
      erp5security_dispatcher.addERP5LoginUserManager('erp5_login_users')
      erp5security_dispatcher.addERP5GroupManager('erp5_groups')
      erp5security_dispatcher.addERP5RoleManager('erp5_roles')
      erp5security_dispatcher.addERP5UserFactory('erp5_user_factory')
      erp5security_dispatcher.addERP5DumbHTTPExtractionPlugin(
                                        'erp5_dumb_http_extraction')
      # Register ERP5UserManager Interface
      p.acl_users.erp5_login_users.manage_activateInterfaces(
                                        ('IAuthenticationPlugin',
                                        'IUserEnumerationPlugin',))
      p.acl_users.erp5_groups.manage_activateInterfaces(('IGroupsPlugin',))
      p.acl_users.erp5_roles.manage_activateInterfaces(('IRolesPlugin',))
      p.acl_users.erp5_user_factory.manage_activateInterfaces(
                                        ('IUserFactoryPlugin',))
      p.acl_users.erp5_dumb_http_extraction.manage_activateInterfaces(
                                        ('IExtractionPlugin',))

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
      assert not p.hasObject('portal_activities')
      addERP5Tool(p, 'portal_activities', 'Activity Tool')
      # Initialize Activities
      p.portal_activities.manageClearActivities()
      # Reindex already existing tools
      for e in p.objectValues():
        try:
          e.reindexObject()
        except TypeError:
          pass

    if not p.hasObject('content_type_registry'):
      self.setupMimetypes(p)

    if not update:
      self.setupWorkflow(p)
      self.setupERP5Core(p,**kw)
      self.setupERP5Promise(p,**kw)

    # Make sure the cache is initialized
    p.portal_caches.updateCache()

    self.setupLastTools(p, **kw)

    # Make sure tools are cleanly indexed with a uid before creating children
    # XXX for some strange reason, member was indexed 5 times
    if not update:
      self.setupIndex(p, **kw)

  def setupERP5Core(self,p,**kw):
    """
    Install the core part of ERP5
    """
    template_tool = p.portal_templates
    if template_tool.getInstalledBusinessTemplate('erp5_core') is None:
      for bt in ('erp5_property_sheets', 'erp5_core', p.erp5_catalog_storage, 'erp5_jquery',
                 'erp5_xhtml_style'):
        if not bt:
          continue
        url = getBootstrapBusinessTemplateUrl(bt)
        bt = template_tool.download(url)
        bt.install(**kw)

  def setupERP5Promise(self,p,**kw):
    """
    Install the ERP5 promise configurator
    """
    template_tool = p.portal_templates
    # Configure the bt5 repository
    repository = p.getPromiseParameter('portal_templates', 'repository')
    if repository is not None:
      template_tool.updateRepositoryBusinessTemplateList(repository.split())
      template_tool.installBusinessTemplateListFromRepository(
          ['erp5_promise'], activate=True, install_dependency=True)
      p.portal_alarms.subscribe()


# Zope offers no mechanism to extend AppInitializer so let's monkey-patch.
AppInitializer_initialize = AppInitializer.initialize.__func__
def initialize(self):
  AppInitializer.initialize = AppInitializer_initialize
  self.initialize()
  try:
    kw = getConfiguration().product_config['initsite']
  except KeyError:
    return
  meta_type = ERP5Site.meta_type
  for _ in self.getApp().objectIds(meta_type):
    return

  # We defer the call to manage_addERP5Site via TimerService because:
  # - we use ZPublisher so that get_request() works
  #   (see Localizer patch)
  # - we want errors to be logged correctly
  #   (see Zope2.zpublisher_exception_hook in Zope2.App.startup)
  import inspect, sys, time
  from AccessControl.SecurityManagement import newSecurityManager
  from App.ZApplication import ZApplicationWrapper
  from Products.ZMySQLDA.db import DB, OperationalError
  def addERP5Site(REQUEST):
    default_kw = inspect.getcallargs(manage_addERP5Site, None, '')
    db = (kw.get('erp5_sql_connection_string') or
      default_kw['erp5_sql_connection_string'])
    # The lock is to avoid that multiple zopes try to create a site when
    # they're started at the same time, because this is a quite long operation
    # (-> high probably of conflict with a lot of wasted CPU).
    # Theoretically, the same precaution should be taken for previous initial
    # commits, but they're small operations. At worst, SlapOS restarts zopes
    # automatically.
    # A ZODB lock would be better but unless we extend ZODB, this is only
    # possible with NEO, by voting a change to oid 0 in a parallel transaction
    # (and abort at the end): thanks to locking at object-level, this would not
    # block the main transaction.
    app = last = None
    while 1:
      try:
        with DB(db).lock():
          transaction.begin()
          app = REQUEST['PARENTS'][0]
          if isinstance(app, ZApplicationWrapper):
            # BBB: With ZServer, it is not loaded yet.
            app = REQUEST['PARENTS'][0] = app()
          for _ in app.objectIds(meta_type):
            return
          uf = app.acl_users
          user = uf.getUser(kw['owner'])
          if not user.has_role('Manager'):
            REQUEST.RESPONSE.unauthorized()
          newSecurityManager(None, user.__of__(uf))
          manage_addERP5Site(app.__of__(RequestContainer(REQUEST=REQUEST)),
            **{k: kw.get(k, v) for k, v in default_kw.iteritems()
                               if isinstance(v, str)})
          transaction.get().note('Created ' + meta_type)
          transaction.commit()
          break
      except OperationalError as e:
        if app is not None:
          raise
        # MySQL server not ready (down or user not created).
        e = str(e)
        if last != e:
          last = e
          LOG('ERP5Site', WARNING,
              'MySQL error while trying to create ERP5 site. Retrying...',
              error=1)
        time.sleep(5)
  from Products.TimerService.timerserver.TimerServer import TimerRequest
  def traverse(*args, **kw):
    del TimerRequest.traverse
    return addERP5Site
  TimerRequest.traverse = traverse

AppInitializer.initialize = initialize
