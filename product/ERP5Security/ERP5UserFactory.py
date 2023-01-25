##############################################################################
#
# Copyright (c) 2001 Zope Corporation and Contributors. All Rights
# Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this
# distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
""" Classes: ERP5User, ERP5UserFactory
"""

from Products.ERP5Type.Globals import InitializeClass
from Acquisition import aq_inner, aq_parent
from AccessControl import ClassSecurityInfo
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Products.PluggableAuthService.plugins.BasePlugin import BasePlugin
from Products.PluggableAuthService.utils import classImplements
from Products.PluggableAuthService.interfaces.plugins import IUserFactoryPlugin
from Products.PluggableAuthService.PropertiedUser import PropertiedUser
from Products import ERP5Security
from Products.ERP5Security.ERP5OAuth2ResourceServerPlugin import (
  USER_PROPERTY_TYPE_KEY,
  USER_PROPERTY_TYPE_VALUE,
  USER_PROPERTY_CLIENT_ID_KEY,
  USER_PROPERTY_CLIENT_REFERENCE_KEY,
)

manage_addERP5UserFactoryForm = PageTemplateFile(
    'www/ERP5Security_addERP5UserFactory', globals(),
    __name__='manage_addERP5UserFactoryForm' )

def addERP5UserFactory( dispatcher, id, title=None, REQUEST=None ):
  """ Add a ERP5UserFactory to a Pluggable Auth Service. """

  euf = ERP5UserFactory(id, title)
  dispatcher._setObject(euf.getId(), euf)

  if REQUEST is not None:
    REQUEST['RESPONSE'].redirect( '%s/manage_workspace'
                                  '?manage_tabs_message='
                                  'ERP5UserFactory+added.'
                                     % dispatcher.absolute_url())


class ERP5User(PropertiedUser):
  """ User class that checks the object allows acquisition of local roles the
  ERP5Type way.
  """
  _user_path = None
  _login_path = None

  def getUserValue(self):
    """ -> user document

    Return the document (ex: Person) corresponding to current user.
    """
    result = self._user_path
    if result is not None:
      return self.getPortalObject().unrestrictedTraverse(result)
    # user id may match in more than one PAS plugin, but fail if more than one
    # underlying path is found.
    user_path_set = {x['path'] for x in self.aq_parent.searchUsers(
      exact_match=True,
      id=self.getId(),
    ) if 'path' in x}
    if user_path_set:
      user_path, = user_path_set
      self._user_path = user_path
      return self.getPortalObject().unrestrictedTraverse(user_path)

  def getLoginValue(self):
    """ -> login document

    Return the document (ex: ERP5 Login) corresponding to current user's login.
    """
    result = self._login_path
    if result is not None:
      return self.getPortalObject().unrestrictedTraverse(result)
    # user name may match at most once, or there can be endless ambiguity.
    user_list = [x for x in self.aq_parent.searchUsers(
      exact_match=True,
      login=self.getUserName(),
    ) if 'login_list' in x]
    if user_list:
      user, = user_list
      login, = user['login_list']
      result = self._login_path = login['path']
      return self.getPortalObject().unrestrictedTraverse(result)

  def getLoginValueList(self, portal_type=None, limit=None):
    """ -> list of login documents

    Return the list of login documents belonging to current user.
    """
    # Aggregate all login paths.
    user_path_set = {
      login['path']
      for user in self.aq_parent.searchUsers(
        exact_match=True,
        id=self.getId(),
        login_portal_type=portal_type,
        max_results=limit,
      ) if 'login_list' in user
      for login in user['login_list']
    }
    unrestrictedTraverse = self.getPortalObject().unrestrictedTraverse
    return [unrestrictedTraverse(x) for x in user_path_set]

  def _iterPropertySheetSetWith(self, key, value):
    """
    Iterate property sheets and yield those whose property <key> has the value
    <value>.
    """
    for property_sheet_id in self.listPropertysheets():
      property_sheet = self.getPropertysheet(property_sheet_id)
      if property_sheet.getProperty(
        USER_PROPERTY_TYPE_KEY,
      ) == USER_PROPERTY_TYPE_VALUE:
        yield property_sheet

  def isFromOAuth2Token(self):
    """
    Return whether this user is authenticated using an OAuth2 token.
    """
    for _ in self._iterPropertySheetSetWith(
      key=USER_PROPERTY_TYPE_KEY,
      value=USER_PROPERTY_TYPE_VALUE,
    ):
      return True
    return False

  def getClientId(self):
    """
    Return the OAuth2 Client ID for the current session.
    Returns None if the user is not authenticated using OAuth2.
    """
    # propertied user API is weird...
    client_id_list = []
    for property_sheet in self._iterPropertySheetSetWith(
      key=USER_PROPERTY_TYPE_KEY,
      value=USER_PROPERTY_TYPE_VALUE,
    ):
      client_id_list.append(property_sheet.getProperty(
        USER_PROPERTY_CLIENT_ID_KEY,
      ))
    result, = client_id_list or [None]
    return result

  def getClientReference(self):
    """
    Return the OAuth2 Client ID for the current session.
    Returns None if the user is not authenticated using OAuth2.
    """
    # propertied user API is weird...
    client_reference_list = []
    for property_sheet in self._iterPropertySheetSetWith(
      key=USER_PROPERTY_TYPE_KEY,
      value=USER_PROPERTY_TYPE_VALUE,
    ):
      client_reference_list.append(property_sheet.getProperty(
        USER_PROPERTY_CLIENT_REFERENCE_KEY,
      ))
    result, = client_reference_list or [None]
    return result

InitializeClass(ERP5User)


class ERP5UserFactory(BasePlugin):
  """ PAS plugin for creating users that understand local roles blocking based
  on type information's acquire_local_roles
  """
  meta_type = 'ERP5 User Factory'
  security = ClassSecurityInfo()

  def __init__(self, id, title=None):
    self._id = self.id = id
    self.title = title

  security.declarePrivate('createUser')
  def createUser( self, user_id, name ):
    """ See IUserFactoryPlugin
    """
    return ERP5User(user_id, name)


classImplements( ERP5UserFactory
               , IUserFactoryPlugin
               )

InitializeClass(ERP5UserFactory)
