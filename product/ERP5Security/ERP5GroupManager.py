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
""" Classes: ERP5GroupManager
"""

from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from AccessControl.SecurityManagement import newSecurityManager, getSecurityManager
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Products.PluggableAuthService.plugins.BasePlugin import BasePlugin
from Products.PluggableAuthService.utils import classImplements
from Products.PluggableAuthService.interfaces.plugins import IGroupsPlugin
from Products.ERP5Type.Cache import CachingMethod

from pickle import dumps, loads

from zLOG import LOG

manage_addERP5GroupManagerForm = PageTemplateFile(
    'www/ERP5Security_addERP5GroupManager', globals(), __name__='manage_addERP5GroupManagerForm' )

def addERP5GroupManager( dispatcher, id, title=None, REQUEST=None ):
  """ Add a ERP5GroupManager to a Pluggable Auth Service. """

  egm = ERP5GroupManager(id, title)
  dispatcher._setObject(egm.getId(), egm)

  if REQUEST is not None:
    REQUEST['RESPONSE'].redirect(
                              '%s/manage_workspace'
                              '?manage_tabs_message='
                              'ERP5GroupManager+added.'
                          % dispatcher.absolute_url())

class ERP5GroupManager(BasePlugin):

  """ PAS plugin for dynamically adding Groups
  based on Assignments in ERP5
  """
  meta_type = 'ERP5 Group Manager'

  security = ClassSecurityInfo()

  def __init__(self, id, title=None):

    self._id = self.id = id
    self.title = title

  #
  #   IGroupsPlugin implementation
  #
  def getGroupsForPrincipal(self, principal, request=None):
    """ See IGroupsPlugin.
    """
    def _getGroupsForPrincipal(user_name, path):
      security_category_dict = {} # key is the base_category_list,
                                  # value is the list of fetched categories
      security_group_list = []
      security_definition_dict = {}

      # because we aren't logged in, we have to create our own
      # SecurityManager to be able to access the Catalog
      #FIXME here we assume that the portal owner will always have
      #      enough rights, which might as well be wrong
      newSecurityManager(self, self.getPortalObject().getOwner())

      # To get the complete list of groups, we try to call the
      # ERP5Type_getSecurityCategoryMapping which should return a dict
      # like : {
      #     'script_1':['base_category_1', 'base_category_2', ...],
      #     'script_2':['base_category_1', 'base_category_3', ...]}
      #
      # else, if the script does not exist, falls back to :
      # { 'ERP5Type_getSecurityCategoryFromAssignment':
      #   self.getPortalAssignmentBaseCategoryList()}

      mapping_method = getattr(self,
          'ERP5Type_getSecurityCategoryMapping', None)
      if mapping_method is None:
        security_definition_dict = {
            'ERP5Type_getSecurityCategoryFromAssignment':
            self.getPortalAssignmentBaseCategoryList()
        }
      else:
        security_definition_dict = mapping_method()

      # get the person from its reference
      catalog_result = self.portal_catalog(
          portal_type="Person", reference=user_name)
      if len(catalog_result) != 1: # we won't proceed with groups
        if len(catalog_result) > 1: # configuration is screwed
          raise 'ConsistencyError', 'There is more than one Person whose \
              login is %s : %s' % (user_name,
              repr([r.getObject() for r in catalog_result]))
        else: # no person is linked to this user login
          return ()
      person_object = catalog_result[0].getObject()
      person_id = person_object.getId()

      # Fetch category values from defined scripts
      for method_name, base_category_list in \
          security_definition_dict.items():
        pickled_category_list = dumps(base_category_list)
        method = getattr(self, method_name)
        if not security_category_dict.has_key(pickled_category_list):
          security_category_dict[pickled_category_list] = []
        security_category_dict[pickled_category_list].extend(
            method(base_category_list, person_id, person_object, ''))

      # Get group names from category values
      group_id_generator = getattr(self, 'ERP5Type_asSecurityGroupId')
      for pickled_category_list, category_value_list in \
          security_category_dict.items():
        base_category_list = loads(pickled_category_list)
        for category_dict in category_value_list:
          security_group_list.append(group_id_generator(
              category_order=base_category_list, **category_dict))

      return tuple(security_group_list)

    _getGroupsForPrincipal = CachingMethod(_getGroupsForPrincipal, id='ERP5GroupManager_getGroupsForPrincipal')
    return _getGroupsForPrincipal(user_name=principal.getId(), path=self.getPhysicalPath())



classImplements( ERP5GroupManager
               , IGroupsPlugin
               )

InitializeClass(ERP5GroupManager)
