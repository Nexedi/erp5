##############################################################################
#
# Copyright (c) 2002-2010 Nexedi SARL and Contributors. All Rights Reserved.
#                         Sebastien Robin <seb@nexedi.com>
#                         Romain Courteaud <romain@nexedi.com>
#                         Arnaud Fontaine <arnaud.fontaine@nexedi.com>
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

from Products.ERP5Type.mixin.constraint import ConstraintMixin
from Products.CMFCore.Expression import Expression
from AccessControl import ClassSecurityInfo
from Products.ERP5Type import Permissions, PropertySheet

class CategoryMembershipArityConstraint(ConstraintMixin):
  """
  This constraint checks if an object respects the arity (with or
  without acquisition depending on use_acquisition value).

  This is only relevant for ZODB Property Sheets (filesystem Property
  Sheets rely on Products.ERP5Type.Constraint.CategoryMembershipArity
  instead).

  For example, if we would like to check whether the object respects a
  minimum arity of '1' and a maximum arity of '1 for the Portal Type
  'Organisation' and the Base Category 'source', then we would create
  a 'Category Membership Arity Constraint' within that Property Sheet
  and set 'Minimum arity' to '1', 'Maximum Arity' to '1', 'Portal
  Types' to 'Organisation', 'Base Categories' to 'source', then set
  the 'Predicate' if necessary (known as 'condition' for filesystem
  Property Sheets).
  """
  meta_type = 'ERP5 Category Membership Arity Constraint'
  portal_type = 'Category Membership Arity Constraint'

  __compatibility_class_name__ = 'CategoryMembershipArity'

  # Declarative security
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  property_sheets = ConstraintMixin.property_sheets + \
                    (PropertySheet.CategoryMembershipArityConstraint,)

  def _calculateArity(self, obj, base_category_list, portal_type_list):
    return len(obj.getCategoryMembershipList(base_category_list,
                                             portal_type=portal_type_list))

  def _checkConsistency(self, obj, fixit=0):
    """
    Check the object's consistency. We are looking at the definition
    of the constraint where the minimum and the maximum arities are
    defined, and the list of objects we wants to check the arity for
    """
    # Retrieve configuration values from PropertySheet
    base_category_list = self.getConstraintBaseCategoryList()
    min_arity = self.getMinArity()
    max_arity = self.getMaxArity()
    portal_type_list = self._getExpressionValue(obj,
                                                self.getConstraintPortalType())

    # Check arity and compare it with the min and max
    arity = self._calculateArity(obj, base_category_list, portal_type_list)
    if (max_arity is None and min_arity <= arity) or \
       min_arity <= arity <= max_arity:
      return []

    mapping = dict(base_category=base_category_list,
                   portal_type=str(portal_type_list),
                   current_arity=arity,
                   min_arity=min_arity,
                   max_arity=max_arity)

    # Generate an error message
    if len(portal_type_list) == 0:
      if max_arity is None:
        message_id = 'message_arity_with_portal_type_too_small'
      else:
        message_id = 'message_arity_with_portal_type_not_in_range'
    else:
      if max_arity is None:
        message_id = 'message_arity_too_small'
      else:
        message_id = 'message_arity_not_in_range'

    return [self._generateError(obj,
                                self._getMessage(message_id),
                                mapping)]


  _message_id_tuple = ('message_arity_too_small',
                       'message_arity_not_in_range',
                       'message_arity_with_portal_type_too_small',
                       'message_arity_with_portal_type_not_in_range')

  @staticmethod
  def _preConvertBaseFromFilesystemDefinition(filesystem_definition_dict):
    """
    CategoryAcquiredMembershipArity and CategoryMembershipArity
    filesystem Constraints have been merged into a single Document for
    ZODB Constraint by adding 'use_acquisition' attribute
    """
    return dict(use_acquisition=(filesystem_definition_dict['type'] == \
                                 'CategoryAcquiredMembershipArity'))

  @staticmethod
  def _convertFromFilesystemDefinition(min_arity,
                                       portal_type=(),
                                       max_arity=None,
                                       base_category=()):
    """
    @see ERP5Type.mixin.constraint.ConstraintMixin._convertFromFilesystemDefinition

    Filesystem definition example:
    { 'id'            : 'source',
      'description'   : '',
      'type'          : 'CategoryMembershipArity',
      'min_arity'     : '1',
      'max_arity'     : '1',
      'portal_type'   : ('Organisation', ),
      'base_category' : ('source',)
      'condition'     : 'python: object.getPortalType() == 'Foo',
    }
    """
    constraint_portal_type_str = isinstance(portal_type, Expression) and \
        portal_type.text or 'python: ' + repr(portal_type)

    zodb_property_dict = dict(
      min_arity=int(min_arity),
      constraint_portal_type=constraint_portal_type_str,
      constraint_base_category_list=base_category)

    if max_arity is not None:
      zodb_property_dict['max_arity'] = int(max_arity)

    yield zodb_property_dict

  def exportToFilesystemDefinitionDict(self):
    filesystem_definition_dict = super(CategoryMembershipArityConstraint,
                                       self).exportToFilesystemDefinitionDict()

    # There is only one ZODB Constraint class for filesystem
    # Constraints CategoryMembershipArity and
    # CategoryAcquiredMembershipArity constraints
    if self.getUseAcquisition():
      filesystem_definition_dict['type'] = 'CategoryAcquiredMembershipArity'

    filesystem_definition_dict['min_arity'] = str(self.getMinArity())

    if self.hasMaxArity():
      filesystem_definition_dict['max_arity'] = str(self.getMaxArity())

    filesystem_definition_dict['portal_type'] = \
        Expression(self.getConstraintPortalType())

    filesystem_definition_dict['base_category'] = self.getConstraintBaseCategoryList()

    return filesystem_definition_dict
