# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2005 Nexedi SARL and Contributors. All Rights Reserved.
#                    Jerome Perrin <jerome@nexedi.com>
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################

from AccessControl import ClassSecurityInfo
from AccessControl.SecurityManagement import getSecurityManager,\
                          setSecurityManager, newSecurityManager
from MethodObject import Method
from Products.ERP5Type.Globals import InitializeClass, DTMLFile
from zLOG import LOG, PROBLEM

from Products.CMFCore.utils import getToolByName
from Products.ERP5Type.Tool.BaseTool import BaseTool
from Products.ERP5Type import Permissions
from Products.ERP5Type.Cache import CachingMethod
from Products.ERP5Type.Utils import convertToUpperCase
from Products.ERP5Type.TransactionalVariable import getTransactionalVariable
from Products.ERP5Form import _dtmldir
from BTrees.OIBTree import OIBTree

_marker = object()

class Priority:
  """ names for priorities """
  SITE  = 1
  GROUP = 2
  USER  = 3

class func_code: pass

class PreferenceMethod(Method):
  """ A method object that lookup the attribute on preferences. """
  # This is required to call the method form the Web
  func_code = func_code()
  func_code.co_varnames = ('self', )
  func_code.co_argcount = 1
  func_defaults = ()

  def __init__(self, attribute, default):
    self.__name__ = self._preference_getter = attribute
    self._preference_default = default
    self._preference_cache_id = 'PreferenceTool.CachingMethod.%s' % attribute

  def __call__(self, instance, default=_marker, *args, **kw):
    def _getPreference(default, *args, **kw):
      # XXX: sql_catalog_id is passed when calling getPreferredArchive
      # This is inconsistent with regular accessor API, and indicates that
      # there is a design problem in current archive API.
      sql_catalog_id = kw.pop('sql_catalog_id', None)
      for pref in instance._getSortedPreferenceList(sql_catalog_id=sql_catalog_id):
        value = getattr(pref, self._preference_getter)(_marker, *args, **kw)
        # XXX Due to UI limitation, null value is treated as if the property
        #     was not defined. The drawback is that it is not possible for a
        #     user to mask a non-null global value with a null value.
        if value not in (_marker, None, '', (), []):
          return value
      if default is _marker:
        return self._preference_default
      return default
    _getPreference = CachingMethod(_getPreference,
            id='%s.%s' % (self._preference_cache_id,
                          instance.getPortalObject().portal_preferences._getCacheId()),
            cache_factory='erp5_ui_long')
    return _getPreference(default, *args, **kw)


class PreferenceTool(BaseTool):
  """
    PreferenceTool manages User Preferences / User profiles.

    TODO:
      - make the preference tool an action provider (templates)
  """
  id            = 'portal_preferences'
  meta_type     = 'ERP5 Preference Tool'
  portal_type   = 'Preference Tool'
  title         = 'Preferences'
  allowed_types = ( 'ERP5 Preference',)
  security      = ClassSecurityInfo()

  aq_preference_generated = False

  security.declareProtected(
       Permissions.ManagePortal, 'manage_overview' )
  manage_overview = DTMLFile( 'explainPreferenceTool', _dtmldir )

  security.declarePrivate('manage_afterAdd')
  def manage_afterAdd(self, item, container) :
    """ init the permissions right after creation """
    item.manage_permission(Permissions.AddPortalContent,
          ['Member', 'Author', 'Manager'])
    item.manage_permission(Permissions.AddPortalFolders,
          ['Member', 'Author', 'Manager'])
    item.manage_permission(Permissions.View,
          ['Member', 'Auditor', 'Manager'])
    item.manage_permission(Permissions.CopyOrMove,
          ['Member', 'Auditor', 'Manager'])
    item.manage_permission(Permissions.ManageProperties,
          ['Manager'], acquire=0)
    item.manage_permission(Permissions.SetOwnPassword,
          ['Member', 'Author', 'Manager'])
    BaseTool.inheritedAttribute('manage_afterAdd')(self, item, container)

  security.declarePublic('getPreference')
  def getPreference(self, pref_name, default=_marker) :
    """ get the preference on the most appopriate Preference object. """
    method = getattr(self, 'get%s' % convertToUpperCase(pref_name), None)
    if method is not None:
      return method(default)
    if default is _marker:
      return None
    return default

  security.declareProtected(Permissions.ModifyPortalContent, "setPreference")
  def setPreference(self, pref_name, value) :
    """ set the preference on the active Preference object"""
    self.getActivePreference()._edit(**{pref_name:value})

  def _getSortedPreferenceList(self, sql_catalog_id=None):
    """ return the most appropriate preferences objects,
        sorted so that the first in the list should be applied first
    """
    tv = getTransactionalVariable()
    security_manager = getSecurityManager()
    user = security_manager.getUser()
    acl_users = self.getPortalObject().acl_users
    try:
      # reset a security manager without any proxy role or unrestricted method,
      # wich affects the catalog search that we do to find applicable
      # preferences.
      actual_user = acl_users.getUserById(user.getId())
      if actual_user is not None:
        newSecurityManager(None, actual_user.__of__(acl_users))
      tv_key = 'PreferenceTool._getSortedPreferenceList/%s/%s' % (user.getId(),
                                                                  sql_catalog_id)
      if tv.get(tv_key, None) is None:
        prefs = []
        # XXX will also cause problems with Manager (too long)
        # XXX For manager, create a manager specific preference
        #                  or better solution
        user_is_manager = 'Manager' in user.getRolesInContext(self)
        for pref in self.searchFolder(portal_type='Preference', sql_catalog_id=sql_catalog_id):
          pref = pref.getObject()
            # XXX quick workaround so that managers only see user preference
            #     they actually own.
          if pref is not None and (not user_is_manager or
                                   pref.getPriority() != Priority.USER or
                                   pref.getOwnerTuple()[1] == user.getId()):
            if pref.getProperty('preference_state',
                                'broken') in ('enabled', 'global'):
                prefs.append(pref)
        prefs.sort(key=lambda x: x.getPriority(), reverse=True)
        # add system preferences before user preferences
        sys_prefs = [x.getObject() for x in self.searchFolder(portal_type='System Preference', sql_catalog_id=sql_catalog_id) \
                     if x.getObject().getProperty('preference_state', 'broken') in ('enabled', 'global')]
        sys_prefs.sort(key=lambda x: x.getPriority(), reverse=True)
        preference_list = sys_prefs + prefs
        tv[tv_key] = preference_list
      return tv[tv_key]
    finally:
      setSecurityManager(security_manager)

  def _getActivePreferenceByPortalType(self, portal_type):
    enabled_prefs = self._getSortedPreferenceList()
    if len(enabled_prefs) > 0 :
      try:
        return [x for x in enabled_prefs
            if x.getPortalType() == portal_type][0]
      except IndexError:
        pass
    return None

  security.declareProtected(Permissions.View, 'getActivePreference')
  def getActivePreference(self) :
    """ returns the current preference for the user.
       Note that this preference may be read only. """
    return self._getActivePreferenceByPortalType('Preference')

  security.declareProtected(Permissions.View, 'clearCache')
  def clearCache(self, preference):
    """ clear cache when a preference is modified.
    This is called by an interaction workflow on preferences.
    """
    self._getCacheId() # initialize _preference_cache if needed.
    if preference.getPriority() == Priority.USER:
      user_id = getSecurityManager().getUser().getId()
      self._preference_cache[user_id] = \
          self._preference_cache.get(user_id, 0) + 1
    self._preference_cache[None] = self._preference_cache.get(None, 0) + 1

  def _getCacheId(self):
    """Return a cache id for preferences.

    We use:
     - user_id: because preferences are always different by user
     - self._preference_cache[user_id] which is increased everytime a user
       preference is modified
     - self._preference_cache[None] which is increased everytime a global
       preference is modified
    """
    user_id = getSecurityManager().getUser().getId()
    try:
      self._preference_cache
    except AttributeError:
      self._preference_cache = OIBTree()
    return self._preference_cache.get(None), self._preference_cache.get(user_id), user_id

  security.declareProtected(Permissions.View, 'getActiveUserPreference')
  def getActiveUserPreference(self) :
    """ returns the current user preference for the user.
    If no preference exists, then try to create one with `createUserPreference`
    type based method.

    This method returns a preference that the user will be able to edit or
    None, if `createUserPreference` refused to create a preference.

    It is intendended for "click here to edit your preferences" actions.
    """
    active_preference = self.getActivePreference()
    if active_preference is None or active_preference.getPriority() != Priority.USER:
      # If user does not have a preference, let's try to create one
      user = self.getPortalObject().portal_membership.getAuthenticatedMember().getUserValue()
      if user is not None:
        createUserPreference = user.getTypeBasedMethod('createUserPreference')
        if createUserPreference is not None:
          active_preference = createUserPreference()
    return active_preference

  security.declareProtected(Permissions.View, 'getActiveSystemPreference')
  def getActiveSystemPreference(self) :
    """ returns the current system preference for the user.
       Note that this preference may be read only. """
    return self._getActivePreferenceByPortalType('System Preference')

  security.declareProtected(Permissions.View, 'getDocumentTemplateList')
  def getDocumentTemplateList(self, folder=None) :
    """ returns all document templates that are in acceptable Preferences
        based on different criteria such as folder, portal_type, etc.
    """
    if folder is None:
      # as the preference tool is also a Folder, this method is called by
      # page templates to get the list of document templates for self.
      folder = self

    # We must set the user_id as a parameter to make sure each
    # user can get a different cache
    def _getDocumentTemplateList(user_id, portal_type=None):
      acceptable_template_list = []
      for pref in self._getSortedPreferenceList() :
        for doc in pref.contentValues(portal_type=portal_type) :
          acceptable_template_list.append(doc.getRelativeUrl())
      return acceptable_template_list
    _getDocumentTemplateList = CachingMethod(_getDocumentTemplateList,
                          'portal_preferences.getDocumentTemplateList',
                                             cache_factory='erp5_ui_short')

    allowed_content_types = map(lambda pti: pti.id,
                                folder.allowedContentTypes())
    user_id = getToolByName(self, 'portal_membership').getAuthenticatedMember().getId()
    template_list = []
    for portal_type in allowed_content_types:
      for template_url in _getDocumentTemplateList(user_id, portal_type=portal_type):
        template = self.restrictedTraverse(template_url, None)
        if template is not None:
          template_list.append(template)
    return template_list

  security.declareProtected(Permissions.ManagePortal,
                            'createActiveSystemPreference')
  def createActiveSystemPreference(self):
    """ Create a System Preference and enable it if there is no other
        enabled System Preference in present.
    """
    if self.getActiveSystemPreference() is not None:
      raise ValueError("Another Active Preference already exists.")
    system_preference = self.newContent(portal_type='System Preference')
    system_preference.enable()

  security.declareProtected(Permissions.ManagePortal,
                            'createPreferenceForUser')
  def createPreferenceForUser(self, user_id, enable=True):
    """Creates a preference for a given user, and optionnally enable the
    preference.
    """
    user_folder = self.acl_users
    user = user_folder.getUserById(user_id)
    if user is None:
      raise ValueError("User %r not found" % (user_id, ))
    security_manager = getSecurityManager()
    try:
      newSecurityManager(None, user.__of__(user_folder))
      preference = self.newContent(portal_type='Preference')
      if enable:
        preference.enable()
      return preference
    finally:
      setSecurityManager(security_manager)

  security.declarePublic('isAuthenticationPolicyEnabled')
  def isAuthenticationPolicyEnabled(self) :
    """
    Return True if authentication policy is enabled.
    This method exists here due to bootstrap issues.
    It should work even if erp5_authentication_policy bt5 is not installed.
    """
    # XXX: define an interface
    def _isAuthenticationPolicyEnabled():
      portal_preferences = self.getPortalObject().portal_preferences
      method_id = 'isPreferredAuthenticationPolicyEnabled'
      method = getattr(self, method_id, None)
      if method is not None and method():
        return True
      return False

    tv = getTransactionalVariable()
    tv_key = 'PreferenceTool._isAuthenticationPolicyEnabled.%s' % getSecurityManager().getUser().getId()
    if tv.get(tv_key, None) is None:
      _isAuthenticationPolicyEnabled = CachingMethod(_isAuthenticationPolicyEnabled,
                                                     id='PortalPreferences_isAuthenticationPolicyEnabled',
                                                     cache_factory='erp5_content_short')
      tv[tv_key] = _isAuthenticationPolicyEnabled()
    return tv[tv_key]


InitializeClass(PreferenceTool)

