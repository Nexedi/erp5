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

from Products.ERP5Type.Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Products.PluggableAuthService.plugins.BasePlugin import BasePlugin
from Products.PluggableAuthService.utils import classImplements
from Products.PluggableAuthService.interfaces.plugins import IGroupsPlugin
from Products.ERP5Type.Cache import CachingMethod
from Products.ERP5Type.ERP5Type \
  import ERP5TYPE_SECURITY_GROUP_ID_GENERATION_SCRIPT
from Products.ERP5Type.UnrestrictedMethod import UnrestrictedMethod
from Products.ZSQLCatalog.SQLCatalog import SimpleQuery
from ZODB.POSException import ConflictError

from zLOG import LOG, WARNING

from Products import ERP5Security
import six

# It can be useful to set NO_CACHE_MODE to 1 in order to debug
# complex security issues related to caching groups. For example,
# the use of scripts instead of external methods for
# assignment category lookup may make the system unstable and
# hard to debug. Setting NO_CACHE_MODE allows to debug such
# issues.
NO_CACHE_MODE = 0

class ConsistencyError(Exception): pass

manage_addERP5GroupManagerForm = PageTemplateFile(
    'www/ERP5Security_addERP5GroupManager', globals(),
    __name__='manage_addERP5GroupManagerForm' )

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
  security.declarePrivate('getGroupsForPrincipal')
  def getGroupsForPrincipal(self, principal, request=None):
    """ See IGroupsPlugin.
    """
    # If this is the super user, skip the check.
    if principal.getId() == ERP5Security.SUPER_USER:
      return ()

    @UnrestrictedMethod
    def _getGroupsForPrincipal(user_id, path):
      user_path_set = {
        x['path']
        for x in self.searchUsers(id=user_id, exact_match=True)
        if 'path' in x
      }
      if not user_path_set:
        return ()
      user_path, = user_path_set
      user_value = self.getPortalObject().unrestrictedTraverse(user_path)
      security_category_dict = {}
      for method_name, base_category_list in self.getPortalSecurityCategoryMapping():
        base_category_list = tuple(base_category_list)
        security_category_list = security_category_dict.setdefault(
          base_category_list,
          [],
        )
        try:
          # The called script may want to distinguish if it is called
          # from here or from _updateLocalRolesOnSecurityGroups.
          # Currently, passing portal_type='' (instead of 'Person')
          # is the only way to make the difference.
          security_category_list.extend(
            getattr(self, method_name)(
              base_category_list,
              user_id,
              user_value,
              '',
            )
          )
        except ConflictError:
          raise
        except Exception:
          LOG(
            'ERP5GroupManager',
            WARNING,
            'could not get security categories from %s' % (method_name, ),
            error=True,
          )

      # Get group names from category values
      # XXX try ERP5Type_asSecurityGroupIdList first for compatibility
      generator_name = 'ERP5Type_asSecurityGroupIdList'
      group_id_list_generator = getattr(self, generator_name, None)
      if group_id_list_generator is None:
        generator_name = ERP5TYPE_SECURITY_GROUP_ID_GENERATION_SCRIPT
        group_id_list_generator = getattr(self, generator_name, None)
      security_group_list = []
      for base_category_list, category_value_list in six.iteritems(security_category_dict):
        for category_dict in category_value_list:
          try:
            group_id_list = group_id_list_generator(
              category_order=base_category_list,
              **category_dict
            )
            if isinstance(group_id_list, str):
              group_id_list = [group_id_list]
            security_group_list.extend(group_id_list)
          except ConflictError:
            raise
          except Exception:
            LOG(
              'ERP5GroupManager',
              WARNING,
              'could not get security groups from %s' % (generator_name, ),
              error=True,
            )
      return tuple(security_group_list)

    if not NO_CACHE_MODE:
      _getGroupsForPrincipal = CachingMethod(_getGroupsForPrincipal,
                                             id='ERP5GroupManager_getGroupsForPrincipal',
                                             cache_factory='erp5_content_short')

    return _getGroupsForPrincipal(
                user_id=principal.getId(),
                path=self.getPhysicalPath())


classImplements( ERP5GroupManager
               , IGroupsPlugin
               )

InitializeClass(ERP5GroupManager)
