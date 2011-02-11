# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2010 Nexedi SA and Contributors. All Rights Reserved.
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsibility of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# guarantees and support are strongly adviced to contract a Free Software
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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
##############################################################################

from zLOG import LOG, PROBLEM, WARNING
from Products.ERP5Type.Globals import InitializeClass
from AccessControl import ClassSecurityInfo
import sys

from AccessControl.SecurityManagement import newSecurityManager,\
    getSecurityManager, setSecurityManager
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Products.PluggableAuthService.PluggableAuthService import \
    _SWALLOWABLE_PLUGIN_EXCEPTIONS
from Products.PluggableAuthService.interfaces import plugins
from Products.PluggableAuthService.utils import classImplements
from Products.PluggableAuthService.plugins.BasePlugin import BasePlugin
from Products.ERP5Type.Cache import transactional_cached
from Products.ERP5Security.ERP5UserManager import SUPER_USER
from ZODB.POSException import ConflictError
from Products.PluggableAuthService.PluggableAuthService import DumbHTTPExtractor
from Products.ERP5Security.ERP5GroupManager import ConsistencyError, NO_CACHE_MODE
from Products.ERP5Type.ERP5Type \
  import ERP5TYPE_SECURITY_GROUP_ID_GENERATION_SCRIPT
from Products.ERP5Type.Cache import CachingMethod

#Form for new plugin in ZMI
manage_addVifibMachineAuthenticationPluginForm = PageTemplateFile(
  'www/Vifib_addVifibMachineAuthenticationPlugin', globals(),
  __name__='manage_addVifibMachineAuthenticationPluginForm')

def addVifibMachineAuthenticationPlugin(dispatcher, id, title=None, REQUEST=None):
  """ Add a VifibMachineAuthenticationPlugin to a Pluggable Auth Service. """

  plugin = VifibMachineAuthenticationPlugin(id, title)
  dispatcher._setObject(plugin.getId(), plugin)

  if REQUEST is not None:
      REQUEST['RESPONSE'].redirect(
          '%s/manage_workspace'
          '?manage_tabs_message='
          'VifibMachineAuthenticationPlugin+added.'
          % dispatcher.absolute_url())

@transactional_cached(lambda portal, *args: args)
def getUserByLogin(portal, login):
  if isinstance(login, basestring):
    login = login,
  result = portal.portal_catalog.unrestrictedSearchResults(
      select_expression='reference',
      portal_type=["Computer", "Software Instance"],
      validation_state="validated",
      reference=dict(query=login, key='ExactMatch'))
  # XXX: Here, we filter catalog result list ALTHOUGH we did pass
  # parameters to unrestrictedSearchResults to restrict result set.
  # This is done because the following values can match person with
  # reference "foo":
  # "foo " because of MySQL (feature, PADSPACE collation):
  #  mysql> SELECT reference as r FROM catalog
  #      -> WHERE reference="foo      ";
  #  +-----+
  #  | r   |
  #  +-----+
  #  | foo |
  #  +-----+
  #  1 row in set (0.01 sec)
  # "bar OR foo" because of ZSQLCatalog tokenizing searched strings
  #  by default (feature).
  return [x.getObject() for x in result if x['reference'] in login]


class VifibMachineAuthenticationPlugin(BasePlugin):
  """
  Plugin to authenicate as machines.
  """

  meta_type = "Vifib Machine Authentication Plugin"
  security = ClassSecurityInfo()

  def __init__(self, id, title=None):
    #Register value
    self._setId(id)
    self.title = title

  ####################################
  #ILoginPasswordHostExtractionPlugin#
  ####################################
  security.declarePrivate('extractCredentials')
  def extractCredentials(self, request):
    """ Extract credentials from the request header. """
    creds = {}
    getHeader = getattr(request, 'getHeader', None)
    if getHeader is None:
      # use get_header instead for Zope-2.8
      getHeader = request.get_header
    user_id = getHeader('REMOTE_USER')
    if user_id is not None:
      creds['machine_login'] = user_id
      creds['remote_host'] = request.get('REMOTE_HOST', '')
      try:
        creds['remote_address'] = request.getClientAddr()
      except AttributeError:
        creds['remote_address'] = request.get('REMOTE_ADDR', '')
      return creds
    else:
      # fallback to default way
      return DumbHTTPExtractor().extractCredentials(request)

  ################################
  #     IAuthenticationPlugin    #
  ################################
  security.declarePrivate('authenticateCredentials')
  def authenticateCredentials(self, credentials):
    """Authentificate with credentials"""
    login = credentials.get('machine_login', None)
    # Forbidden the usage of the super user.
    if login == SUPER_USER:
      return None

    #Search the user by his login
    user_list = self.getUserByLogin(login)
    if len(user_list) != 1:
      return None
    return (login, login)

  def getUserByLogin(self, login):
    # Search the Catalog for login and return a list of person objects
    # login can be a string or a list of strings
    # (no docstring to prevent publishing)
    if not login:
      return []
    if isinstance(login, list):
      login = tuple(login)
    elif not isinstance(login, tuple):
      login = str(login)
    try:
      return getUserByLogin(self.getPortalObject(), login)
    except ConflictError:
      raise
    except:
      LOG('VifibMachineAuthenticationPlugin', PROBLEM, 'getUserByLogin failed',
        error=sys.exc_info())
      # Here we must raise an exception to prevent callers from caching
      # a result of a degraded situation.
      # The kind of exception does not matter as long as it's catched by
      # PAS and causes a lookup using another plugin or user folder.
      # As PAS does not define explicitely such exception, we must use
      # the _SWALLOWABLE_PLUGIN_EXCEPTIONS list.
      raise _SWALLOWABLE_PLUGIN_EXCEPTIONS[0]

  #################################
  #   IGroupsPlugin               #
  #################################
  # This is patched version of
  #   Products.ERP5Security.ERP5GroupManager.ERP5GroupManager.getGroupsForPrincipal
  # which allows to treat Computer and Software Instance as loggable user
  loggable_portal_type_list = ['Computer', 'Person', 'Software Instance']
  def getGroupsForPrincipal(self, principal, request=None):
    """ See IGroupsPlugin.
    """
    # If this is the super user, skip the check.
    if principal.getId() == SUPER_USER:
      return ()

    def _getGroupsForPrincipal(user_name, path):
      security_category_dict = {} # key is the base_category_list,
                                  # value is the list of fetched categories
      security_group_list = []
      security_definition_list = ()

      # because we aren't logged in, we have to create our own
      # SecurityManager to be able to access the Catalog
      sm = getSecurityManager()
      if sm.getUser().getId() != SUPER_USER:
        newSecurityManager(self, self.getUser(SUPER_USER))
      try:
        # To get the complete list of groups, we try to call the
        # ERP5Type_getSecurityCategoryMapping which should return a list
        # of lists of two elements (script, base_category_list) like :
        # (
        #   ('script_1', ['base_category_1', 'base_category_2', ...]),
        #   ('script_2', ['base_category_1', 'base_category_3', ...])
        # )
        #
        # else, if the script does not exist, falls back to a list containng
        # only one list :
        # (('ERP5Type_getSecurityCategoryFromAssignment',
        #   self.getPortalAssignmentBaseCategoryList() ),)

        mapping_method = getattr(self,
            'ERP5Type_getSecurityCategoryMapping', None)
        if mapping_method is None:
          security_definition_list = ((
              'ERP5Type_getSecurityCategoryFromAssignment',
              self.getPortalAssignmentBaseCategoryList()
          ),)
        else:
          security_definition_list = mapping_method()

        # get the loggable document from its reference - no security check needed
        catalog_result = self.portal_catalog.unrestrictedSearchResults(
            portal_type=self.loggable_portal_type_list,
            reference=user_name)
        if len(catalog_result) != 1: # we won't proceed with groups
          if len(catalog_result) > 1: # configuration is screwed
            raise ConsistencyError, 'There is more than one of %s whose \
                login is %s : %s' % (','.join(self.loggable_portal_type_list),
                user_name,
                repr([r.getObject() for r in catalog_result]))
          else:
            return ()
        loggable_object = catalog_result[0].getObject()

        # Fetch category values from defined scripts
        for (method_name, base_category_list) in security_definition_list:
          base_category_list = tuple(base_category_list)
          method = getattr(self, method_name)
          security_category_list = security_category_dict.setdefault(
                                            base_category_list, [])
          try:
            # The called script may want to distinguish if it is called
            # from here or from _updateLocalRolesOnSecurityGroups.
            # Currently, passing portal_type='' (instead of 'Person')
            # is the only way to make the difference.
            security_category_list.extend(
              method(base_category_list, user_name, loggable_object, '')
            )
          except ConflictError:
            raise
          except:
            LOG('ERP5GroupManager', WARNING,
                'could not get security categories from %s' % (method_name,),
                error = sys.exc_info())

        # Get group names from category values
        # XXX try ERP5Type_asSecurityGroupIdList first for compatibility
        generator_name = 'ERP5Type_asSecurityGroupIdList'
        group_id_list_generator = getattr(self, generator_name, None)
        if group_id_list_generator is None:
          generator_name = ERP5TYPE_SECURITY_GROUP_ID_GENERATION_SCRIPT
          group_id_list_generator = getattr(self, generator_name)
        for base_category_list, category_value_list in \
            security_category_dict.iteritems():
          for category_dict in category_value_list:
            try:
              group_id_list = group_id_list_generator(
                                        category_order=base_category_list,
                                        **category_dict)
              if isinstance(group_id_list, str):
                group_id_list = [group_id_list]
              security_group_list.extend(group_id_list)
            except ConflictError:
              raise
            except:
              LOG('ERP5GroupManager', WARNING,
                  'could not get security groups from %s' %
                  generator_name,
                  error = sys.exc_info())
      finally:
        setSecurityManager(sm)
      return tuple(security_group_list)

    if not NO_CACHE_MODE:
      _getGroupsForPrincipal = CachingMethod(_getGroupsForPrincipal,
                                             id='ERP5GroupManager_getGroupsForPrincipal',
                                             cache_factory='erp5_content_short')

    return _getGroupsForPrincipal(
                user_name=principal.getId(),
                path=self.getPhysicalPath())

  #
  #   IUserEnumerationPlugin implementation
  #
  security.declarePrivate( 'enumerateUsers' )
  def enumerateUsers(self, id=None, login=None, exact_match=False,
                   sort_by=None, max_results=None, **kw):
    """ See IUserEnumerationPlugin.
    """
    if id is None:
      id = login
    if isinstance(id, str):
      id = (id,)
    if isinstance(id, list):
      id = tuple(id)

    user_info = []
    plugin_id = self.getId()

    id_list = []
    for user_id in id:
      if SUPER_USER == user_id:
        info = { 'id' : SUPER_USER
                , 'login' : SUPER_USER
                , 'pluginid' : plugin_id
                }
        user_info.append(info)
      else:
        id_list.append(user_id)

    if id_list:
      for user in self.getUserByLogin(tuple(id_list)):
          info = { 'id' : user.getReference()
                 , 'login' : user.getReference()
                 , 'pluginid' : plugin_id
                 }

          user_info.append(info)

    return tuple(user_info)

#List implementation of class
classImplements(VifibMachineAuthenticationPlugin,
                plugins.IAuthenticationPlugin)
classImplements( VifibMachineAuthenticationPlugin,
                plugins.ILoginPasswordHostExtractionPlugin
               )
classImplements( VifibMachineAuthenticationPlugin,
               plugins.IGroupsPlugin
               )
classImplements( VifibMachineAuthenticationPlugin,
               plugins.IUserEnumerationPlugin
               )


InitializeClass(VifibMachineAuthenticationPlugin)
