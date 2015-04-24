##############################################################################
#
# Copyright (c) 2002-2009 Nexedi SARL and Contributors. All Rights Reserved.
#                         Julien Muchembled <jm@nexedi.com>
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
""" Information about customizable roles.
"""

import zope.interface
from AccessControl import ClassSecurityInfo
from Acquisition import aq_base
from Products.ERP5Type.Globals import InitializeClass

from Products.CMFCore.Expression import Expression

from Products.ERP5Type import interfaces, Permissions, PropertySheet
from Products.ERP5Type.ERP5Type \
  import ERP5TYPE_SECURITY_GROUP_ID_GENERATION_SCRIPT
from Products.ERP5Type.Permissions import AccessContentsInformation
from Products.ERP5Type.XMLObject import XMLObject
from Products.ERP5Type.gen_id_from_reference import GenerateIdFromReferenceMixin


class RoleInformation(GenerateIdFromReferenceMixin('role'), XMLObject):
  """ Represent a role definition.

  Roles definitions defines local roles on ERP5Type documents. They are
  applied by the updateLocalRolesOnDocument method.
  """
  meta_type = 'ERP5 Role Information'
  portal_type = 'Role Information'
  add_permission = Permissions.AddPortalContent

  security = ClassSecurityInfo()
  security.declareObjectProtected(AccessContentsInformation)

  zope.interface.implements(interfaces.ILocalRoleGenerator)

  # Declarative properties
  property_sheets = ( PropertySheet.CategoryCore
                    , PropertySheet.DublinCore
                    , PropertySheet.RoleInformation
                    )

  security.declarePrivate('testCondition')
  def testCondition(self, ec):
    """Evaluate condition using context, 'ec', and return 0 or 1"""
    condition = self.getCondition()
    return condition is None and 1 or condition(ec)

  def _setCondition(self, value):
    """Overridden setter for 'condition' to accept string and clean null values
    """
    if isinstance(value, basestring):
      value = value and Expression(value) or None
    self._baseSetCondition(value)

  def getCondition(self):
    """Overridden getter for 'condition' to clean null values"""
    if getattr(aq_base(self), 'condition', None) == '':
      del self.condition
    return self._baseGetCondition()

  security.declareProtected(AccessContentsInformation, 'getConditionText')
  def getConditionText(self):
    """Return the text of the condition"""
    return getattr(self.getCondition(), 'text', None)

  security.declareProtected(AccessContentsInformation, 'PrincipiaSearchSource')
  def PrincipiaSearchSource(self):
    """Return keywords for "Find" tab in ZMI"""
    search_source_list = [self.getTitle(),
                         self.getDescription(),
                         self.getConditionText(),
                         self.getRoleBaseCategoryScriptId()]
    return ' '.join(filter(None, search_source_list))

  security.declarePrivate("getLocalRolesFor")
  def getLocalRolesFor(self, ob, user_name=None):
    """Compute the security that should be applied on an object

    Returned value is a dict: {groud_id: role_name_set, ...}
    """
    # get the list of base_categories that are statically defined
    static_base_category_list = [x.split('/', 1)[0]
                                 for x in self.getRoleCategoryList()]
    # get the list of base_categories that are to be fetched through the
    # script
    category_order_list = self.getRoleBaseCategoryList()
    dynamic_base_category_list = [x for x in category_order_list
                                    if x not in static_base_category_list]
    # get the aggregated list of base categories, to preserve the order
    for bc in static_base_category_list:
      if bc not in category_order_list:
        category_order_list.append(bc)

    # get the script and apply it if dynamic_base_category_list is not empty
    if dynamic_base_category_list:
      base_category_script_id = self.getRoleBaseCategoryScriptId()
      base_category_script = getattr(ob, base_category_script_id, None)
      if base_category_script is None:
        raise AttributeError('Script %s was not found to fetch values for'
          ' base categories : %s' % (base_category_script_id,
                                     ', '.join(dynamic_base_category_list)))
      # call the script, which should return either a dict or a list of
      # dicts
      category_result = base_category_script(dynamic_base_category_list,
                                             user_name,
                                             ob,
                                             ob.getPortalType())
      # If we decide in the script that we don't want to update the
      # security for this object, we can just have it return None
      # instead of a dict or list of dicts
      if category_result is None:
        return {}
    else:
      # no base_category needs to be retrieved using the script, we use
      # a list containing an empty dict to trick the system into
      # creating one category_value_dict (which will only use statically
      # defined categories)
      category_result = [{}]

    group_id_role_dict = {}
    role_list = self.getRoleNameList()

    if isinstance(category_result, dict):
      # category_result is a dict (which provide group IDs directly)
      # which represents of mapping of roles, security group IDs
      # XXX explain that this is for providing user IDs mostly
      for role, group_id_list in category_result.iteritems():
        if role in role_list:
          for group_id in group_id_list:
            group_id_role_dict.setdefault(group_id, set()).add(role)
    else:
      group_id_generator = getattr(ob,
        ERP5TYPE_SECURITY_GROUP_ID_GENERATION_SCRIPT)

      # Prepare definition dict once only
      category_definition_dict = {}
      for c in self.getRoleCategoryList():
        bc, value = c.split('/', 1)
        category_definition_dict.setdefault(bc, []).append(value)

      # category_result is a list of dicts that represents the resolved
      # categories we create a category_value_dict from each of these
      # dicts aggregated with category_order and statically defined
      # categories
      for category_dict in category_result:
        category_value_dict = {'category_order':category_order_list}
        category_value_dict.update(category_dict)
        category_value_dict.update(category_definition_dict)
        group_id_list = group_id_generator(**category_value_dict)
        if group_id_list:
          if isinstance(group_id_list, str):
            # Single group is defined (this is usually for group membership)
            # DEPRECATED due to cartesian product requirement
            group_id_list = group_id_list,
          # Multiple groups are defined (list of users
          # or list of group IDs resulting from a cartesian product)
          for group_id in group_id_list:
            group_id_role_dict[group_id] = role_list

    return group_id_role_dict

InitializeClass(RoleInformation)
