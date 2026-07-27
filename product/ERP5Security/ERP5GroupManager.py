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

from contextlib import contextmanager as _cm_dc
from threading import local as _local_dc
_CACHE_ENABLED_LOCAL = _local_dc()
@_cm_dc
def disableCache():
  _CACHE_ENABLED_LOCAL.value = False
  try: yield
  finally: _CACHE_ENABLED_LOCAL.value = True

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

    def _computeSecurityGroupIdSet(user_id, user_value):
      # Run the standard security pipeline (open Assignments -> security
      # category values -> security group id strings) for a single user
      # document, and return the resulting set of security group ids.
      # Factored out of _getGroupsForPrincipal so the Artificial Agent cap
      # below can re-run the *exact same* computation for the owning Person;
      # this is what makes the agent's and the owner's group sets directly
      # comparable. Behaviour for every non-agent principal is unchanged.
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
      return set(security_group_list)

    @UnrestrictedMethod
    def _getGroupsForPrincipal(user_id, path):
      # Note: arguments are just a cache key. user_id is bijective to
      # principal, so its presence in the cache key allows us to access
      # principal.
      user_path_set = {
        x['path']
        for x in self.searchUsers(id=user_id, exact_match=True)
        if 'path' in x
      }
      if not user_path_set:
        return ()
      user_path, = user_path_set
      user_value = self.getPortalObject().unrestrictedTraverse(user_path)
      security_group_set = _computeSecurityGroupIdSet(user_id, user_value)
      # === Artificial Agent security group mask (capping enforcement) ======
      # Invariant (erp5-agent-study/PLAN.md 4.4):
      #   for every document D and every permission P,
      #     allowed(agent, D, P)  =>  allowed(owner, D, P).
      # An Artificial Agent is a technical account owned by exactly one Person
      # (owner link = the 'subordination' category). It must never obtain more
      # effective access than that Person. Security group ids are the sole
      # channel through which Assignments grant local roles (and hence
      # permissions), so restricting the agent's EFFECTIVE group set to its
      # intersection with the owner's group set makes the agent's
      # group-derived principals a subset of the owner's. Because allowed(),
      # getRolesInContext() and catalog listability are all monotonic in the
      # principal group set (more groups can only grant more roles, hence more
      # permissions), the invariant then holds on every surface -- including
      # workflows whose role->permission map inverts the usual ordering (e.g.
      # leave_request_workflow, where Assignee, not Assignor, may modify a
      # draft: see erp5-agent-study/REPORT_ROLE_ORDER_VIOLATIONS.md). Whatever
      # right the agent would gain from a group, it keeps only if the owner
      # holds that same group.
      # Scope: this masks GROUP-derived rights, which is by construction what
      # the Assignment pipeline produces. User-id-targeted local roles (the
      # Owner role seeded on agent-created documents, or a Role Information
      # naming the agent's own user id directly) are outside this layer and are
      # handled separately (study 4.4 accepted-exceptions register E1/E2).
      if user_value.getPortalType() == 'Artificial Agent':
        try:
          owner_value = user_value.getSubordinationValue()
          # Fail closed: an agent with no resolvable Person owner gets NOTHING
          # -- never its own groups. The owner MUST be a Person; a Person never
          # carries a subordination-to-agent, so the owner computation below
          # terminates in a single hop. Any other case (missing owner, or an
          # agent owned by an agent / a cycle) fails closed to an empty set.
          if owner_value is None or owner_value.getPortalType() != 'Person':
            return ()
          owner_user_id = owner_value.getUserId()
          if not owner_user_id:
            return ()
          owner_group_set = _computeSecurityGroupIdSet(owner_user_id, owner_value)
        except ConflictError:
          raise
        except Exception:
          # Any failure resolving or computing the owner's groups must never
          # widen the agent's access: fail closed.
          LOG(
            'ERP5GroupManager',
            WARNING,
            'could not compute owner groups for Artificial Agent %r; '
            'failing closed (empty group set)' % (user_id, ),
            error=True,
          )
          return ()
        security_group_set = security_group_set & owner_group_set
      return tuple(security_group_set)

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
