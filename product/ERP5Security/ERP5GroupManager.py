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

from collections import defaultdict
from contextlib import contextmanager
from threading import local
import warnings
from Products.ERP5Type.Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Products.PluggableAuthService.plugins.BasePlugin import BasePlugin
from Products.PluggableAuthService.utils import classImplements
from Products.PluggableAuthService.interfaces.plugins import IGroupsPlugin
from Products.ERP5Type.Cache import CachingMethod
from Products.ERP5Type.ERP5Type import (
    ERP5TYPE_SECURITY_GROUP_ID_GENERATION_SCRIPT,
    ERP5TYPE_SECURITY_GROUP_ID_GENERATION_SCRIPT_V2,
)
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

_CACHE_ENABLED_LOCAL = local()
@contextmanager
def disableCache():
  """
  Disable ERP5GroupManager.getGroupsForPrincipal internal cache.
  Use when retrieving a user from PAS:
    with disableCache():
      user = user_folder.getUser(...)
  """
  _CACHE_ENABLED_LOCAL.value = False
  try:
    yield
  finally:
    _CACHE_ENABLED_LOCAL.value = True

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
    if (
      principal.getId() == ERP5Security.SUPER_USER or
      # OAuth2 authentication brings its own groups.
      principal.isFromOAuth2Token()
    ):
      return ()

    @UnrestrictedMethod
    def _getGroupsForPrincipal(user_id, path):
      # Note: arguments are just as a cache key. user_id is bijective to
      # principal, so its presence in the cache key allows us to access
      # principal.
      user_value = getattr(principal, 'getUserValue', lambda: None)()
      if user_value is None:
        return ()
      category_mapping = self.getPortalSecurityCategoryMapping()
      if category_mapping: # BBB
        warnings.warn(
          'Consider migrating ERP5Type_getSecurityCategoryMapping to '
          'ERP5User_getUserSecurityCategoryValueList to get better '
          'performance',
          DeprecationWarning,
        )
        has_relative_urls = True
        security_category_dict = defaultdict(list)
        for method_name, base_category_list in category_mapping:
          base_category_list = tuple(base_category_list)
          security_category_list = security_category_dict[base_category_list]
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
      else:
        has_relative_urls = False
        try:
          getUserSecurityCategoryValueList = user_value.ERP5User_getUserSecurityCategoryValueList
        except AttributeError: # BBB
          security_category_value_dict_list = []
        else:
          security_category_value_dict_list = getUserSecurityCategoryValueList()
      security_group_set = set()
      # XXX try ERP5Type_asSecurityGroupIdList first for compatibility
      generator_name = 'ERP5Type_asSecurityGroupIdList'
      group_id_list_generator = getattr(self, generator_name, None)
      if group_id_list_generator is None:
        generator_name = ERP5TYPE_SECURITY_GROUP_ID_GENERATION_SCRIPT
        group_id_list_generator = getattr(self, generator_name, None)
      if group_id_list_generator is None:
        if has_relative_urls:
          # Convert security_category_dict to security_category_value_dict_list
          # Differences with direct security_category_value_dict_list production:
          # - incomplete deduplication
          # - extra intermediate sorting
          getCategoryValue = self.portal_categories.getCategoryValue
          security_category_value_dict_list = (
            dict(x)
            for x in {
              tuple(sorted(
                (
                  (
                    base_category,
                    tuple(
                      (
                        getCategoryValue(base_category + '/' + relative_url.rstrip('*')),
                        relative_url.endswith('*'),
                      )
                      for relative_url in (
                        (relative_url_list, )
                        if isinstance(relative_url_list, str) else
                        sorted(relative_url_list)
                      )
                    )
                  )
                  for (
                    base_category,
                    relative_url_list,
                  ) in six.iteritems(security_dict)
                ),
                # Avoid comparing persistent objects, for performance purposes:
                # these are stored by path.
                key=lambda x: x[0]
              ))
              for security_category_list in six.itervalues(security_category_dict)
              for security_dict in security_category_list
            }
          )
        for security_category_value_dict in security_category_value_dict_list:
          security_group_set.update(
            getattr(self, ERP5TYPE_SECURITY_GROUP_ID_GENERATION_SCRIPT_V2)(
              category_dict=security_category_value_dict,
            ),
          )
      else: # BBB
        warnings.warn(
          'Consider migrating %s to %s to get better performance' % (
            generator_name,
            ERP5TYPE_SECURITY_GROUP_ID_GENERATION_SCRIPT_V2,
          ),
          DeprecationWarning,
        )
        if not has_relative_urls:
          # Convert security_category_value_dict_list to security_category_dict
          # Differences with direct security_category_dict generation:
          # - the order of items in the tuples used as keys is random
          # - repetitions will be missing (which is arguably an improvement)
          security_category_dict = {
            tuple(security_category_value_dict): [
              {
                base_category: [
                  category_value.getRelativeUrl() + ('*' if parent else '')
                  for category_value, parent in category_value_list
                ]
                for base_category, category_value_list in six.iteritems(
                  security_category_value_dict,
                )
              }
            ]
            for security_category_value_dict in security_category_value_dict_list
          }
        # Get group names from category values
        for base_category_list, category_value_list in six.iteritems(security_category_dict):
          for category_dict in category_value_list:
            try:
              group_id_list = group_id_list_generator(
                category_order=base_category_list,
                **category_dict
              )
              if isinstance(group_id_list, str):
                group_id_list = [group_id_list]
              security_group_set.update(group_id_list)
            except ConflictError:
              raise
            except Exception:
              LOG(
                'ERP5GroupManager',
                WARNING,
                'could not get security groups from %s' % (generator_name, ),
                error=True,
              )
      return tuple(security_group_set)

    if not NO_CACHE_MODE and getattr(_CACHE_ENABLED_LOCAL, 'value', True):
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
