##############################################################################
#
# Copyright (c) 2001 Zope Corporation and Contributors. All Rights
# Reserved.
#                  Fabien Morin <fabien@nexedi.com>
#                  Mohamadou Mbengue <mmbengue@gmail.com>
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
""" Classes: ERP5GroupManager
"""

from Products.ERP5Type.Globals import InitializeClass
from AccessControl.SecurityManagement import newSecurityManager,\
    getSecurityManager, setSecurityManager
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from AccessControl import ClassSecurityInfo
from Products.PluggableAuthService.PropertiedUser import PropertiedUser
from Products.PluggableAuthService.plugins.BasePlugin import BasePlugin
from Products.PluggableAuthService.utils import classImplements
from Products.PluggableAuthService.interfaces.plugins import IGroupsPlugin
from Products.ERP5Security.ERP5GroupManager import ERP5GroupManager
from Products.ERP5Type.Cache import CachingMethod
from ZODB.POSException import ConflictError
from Products.ERP5Security.ERP5GroupManager import ConsistencyError

import sys

from zLOG import LOG, WARNING

from Products import ERP5Security


NO_CACHE_MODE = 0
manage_addEGOVGroupManagerForm = PageTemplateFile(
    'www/ERP5Security_addERP5GroupManager', globals(),
    __name__='manage_addERP5GroupManagerForm' )

def addEGOVGroupManager( dispatcher, id, title=None, REQUEST=None ):
  """ Add a EGOVGroupManager to a Pluggable Auth Service. """
  egm = EGOVGroupManager(id, title)
  dispatcher._setObject(egm.getId(), egm)

  if REQUEST is not None:
    REQUEST['RESPONSE'].redirect(
                              '%s/manage_workspace'
                              '?manage_tabs_message='
                              'EGOVGroupManager+added.'
                          % dispatcher.absolute_url())


class EGOVGroupManager(ERP5GroupManager):
  """ PAS plugin for dynamically adding Groups
      this plugin permit to login with evry portal_type
      So it's possible to login with organisation
  """
  meta_type = 'EGOV Group Manager'
  security = ClassSecurityInfo()

  portal_type_list = ('Person',)

  _properties = BasePlugin._properties + (
     {'label' : 'Portal Type List (Experimental)',
       'type' : 'lines',
       'id'   : 'portal_type_list',
       'mode' : 'w',
     },
     )

  def __init__(self, id, title=None):

    self._id = self.id = id
    self.title = title

  #
  #   IGroupsPlugin implementation
  #
  def getGroupsForPrincipal(self, principal, request=None):
    """ See IGroupsPlugin.
    """
    # If this is the super user, skip the check.
    if principal.getId() == ERP5Security.SUPER_USER:
      return ()

    def _getGroupsForPrincipal(user_name, path):
      security_category_dict = {} # key is the base_category_list,
                                  # value is the list of fetched categories
      security_group_list = []
      security_definition_list = ()

      # because we aren't logged in, we have to create our own
      # SecurityManager to be able to access the Catalog
      sm = getSecurityManager()
      if sm.getUser().getId() != ERP5Security.SUPER_USER:
        newSecurityManager(self, self.getUser(ERP5Security.SUPER_USER))
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

        # get the person from its reference - no security check needed
        catalog_result = self.portal_catalog.unrestrictedSearchResults(
            portal_type=self.portal_type_list, reference=user_name)

        if len(catalog_result) != 1: # we won't proceed with groups
          if len(catalog_result) > 1: # configuration is screwed
            raise ConsistencyError, 'There is more than one Person whose \
                login is %s : %s' % (user_name,
                repr([r.getObject() for r in catalog_result]))
          else: # no person is linked to this user login
            portal = self.getPortalObject()

            # this permit to get the module of the application
            # the goal is to work with anonymous applications, even if
            # they are not reindexed

            module_id = self.REQUEST.get('anonymous_module', None)
            if module_id:
              module =  getattr(portal, module_id, None)
              if module is not None:
                result = module._getOb(user_name, None)
                if result is not None:
                  person_object = result
                else:
                  return ()
            else:
              return ()
        else:
          person_object = catalog_result[0].getObject()
        person_id = person_object.getId()

        # Fetch category values from defined scripts
        for (method_name, base_category_list) in security_definition_list:
          base_category_list = tuple(base_category_list)
          method = getattr(self, method_name)
          security_category_list = security_category_dict.setdefault(
                                            base_category_list, [])
          try:
            security_category_list.extend(
              method(base_category_list, user_name, person_object, '')
            )
          except ConflictError:
            raise
          except:
            LOG('EGOVGroupManager', WARNING,
                'could not get security categories from %s' % (method_name,),
                error = sys.exc_info())

        # Get group names from category values
        group_id_list_generator = getattr(self,
                                      'ERP5Type_asSecurityGroupIdList', None)
        if group_id_list_generator is None:
          group_id_list_generator = getattr(self, 'ERP5Type_asSecurityGroupId')
          generator_name = "ERP5Type_asSecurityGroupId"
        else:
          generator_name = 'ERP5Type_asSecurityGroupIdList'
        for base_category_list, category_value_list in \
            security_category_dict.items():
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
              LOG('EGOVGroupManager', WARNING,
                  'could not get security groups from %s' %
                  generator_name,
                  error = sys.exc_info())
      finally:
        setSecurityManager(sm)
      return tuple(security_group_list)

    if not NO_CACHE_MODE:
      _getGroupsForPrincipal = CachingMethod(_getGroupsForPrincipal,
                                 id='EGOVGroupManager_getGroupsForPrincipal',
                                 cache_factory='erp5_content_short')

    return _getGroupsForPrincipal(
                user_name=principal.getId(),
                path=self.getPhysicalPath())


classImplements( EGOVGroupManager
               , IGroupsPlugin
               )

InitializeClass(EGOVGroupManager)
