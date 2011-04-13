##############################################################################
#
# Copyright (c) 2008 Nexedi SA and Contributors. All Rights Reserved.
#                    Romain Courteaud <romain@nexedi.com>
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
from Products.ERP5Type import PropertySheet
from Products.ERP5Type.Utils import createExpressionContext
from Products.ERP5Type.Utils import evaluateExpressionFromString

class CategoryMembershipStateConstraint(ConstraintMixin):
  """This method check if the category membership is in a
  valid workflow state.
  It can check if an order is linked to validated organisation
  through source category.
  """
  meta_type = 'ERP5 Category Membership State Constraint'
  portal_type = 'Category Membership State Constraint'

  property_sheets = ConstraintMixin.property_sheets + \
                    (PropertySheet.CategoryMembershipStateConstraint,)

  _message_id_tuple = ('message_different_state',)


  def _checkConsistency(self, obj, fixit=0):
    """Check the object's consistency.
    """
    error_list = []

    base_category = self.getBaseCategory()
    workflow_variable = self.getWorkflowVariable()
    expression_context = createExpressionContext(obj)
    portal_type_list_expression = self.getMembershipPortalTypeList()
    workflow_state_list_expression = self.getWorkflowStateList()

    portal_type_list = evaluateExpressionFromString(expression_context,
                                                   portal_type_list_expression)
    workflow_state_list = evaluateExpressionFromString(expression_context,
                                                workflow_state_list_expression)

    membership_list = obj.getValueList(base_category,
                                       portal_type=portal_type_list)

    for membership in membership_list:
      current_state = membership.getProperty(workflow_variable)
      if current_state not in workflow_state_list:
        mapping = dict(workflow_variable=workflow_variable,
                       membership_url=membership.getRelativeUrl(),
                       membership_title=membership.getTitle(),
                       current_state=current_state,
                       workflow_state_list=str(workflow_state_list),)
        if getattr(membership, 'getReference', None) is not None:
          mapping['membership_reference'] = membership.getReference()
        message_id = 'message_different_state'

        error_list.append(self._generateError(obj, self._getMessage(message_id),
                                              mapping=mapping)
                         )

    return error_list
