##############################################################################
#
# Copyright (c) 2002 Nexedi SARL and Contributors. All Rights Reserved.
#                    Sebastien Robin <seb@nexedi.com>
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

from AccessControl import ClassSecurityInfo
from Acquisition import aq_base, aq_parent, aq_inner, aq_acquire
from Products.CMFCore.utils import getToolByName

from Products.ERP5Type import Permissions, PropertySheet, Constraint, interfaces
from Products.ERP5.Document.Rule import Rule

from zLOG import LOG, INFO

class PaymentRule(Rule):
  """Payment Rule generates payment simulation movement from invoice
  transaction simulation movements.
  """

  # CMF Type Definition
  meta_type = 'ERP5 Payment Rule'
  portal_type = 'Payment Rule'
  add_permission = Permissions.AddPortalContent

  # Declarative security
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  receivable_account_type_list = ('asset/receivable', )
  payable_account_type_list = ('liability/payable', )

  def _generatePrevisionList(self, applied_rule, **kw):
    """
    Generate a list of dictionaries, that contain calculated content of
    current Simulation Movements in applied rule.
    based on its context (parent movement, delivery, configuration ...)

    These previsions are returned as dictionaries.
    """
    prevision_dict_list = []
    for input_movement, business_path in self \
        ._getInputMovementAndPathTupleList(applied_rule):
      if business_path is None:
        # since Payment Rule does not know what to do without business
        # path, we return empty list here and creates no simulation
        # movements.
        return []
      # Since we need to consider business_path only for bank movement,
      # not for payable movement, we pass None as business_path here.
      kw = self._getExpandablePropertyDict(applied_rule, input_movement, None)
      start_date = business_path.getExpectedStartDate(input_movement)
      if start_date is not None:
        kw['start_date'] = start_date
      stop_date = business_path.getExpectedStopDate(input_movement)
      if stop_date is not None:
        kw['stop_date'] = stop_date
      quantity = business_path.getExpectedQuantity(input_movement)

      # one for payable
      payable_dict = kw.copy()
      payable_dict.update(dict(quantity=-quantity))
      prevision_dict_list.append(payable_dict)
      # one for bank
      bank_dict = kw.copy()
      bank_dict.update(dict(quantity=quantity,
                            source=business_path.getSource(),
                            destination=business_path.getDestination()))
      prevision_dict_list.append(bank_dict)
    return prevision_dict_list

  security.declareProtected(Permissions.ModifyPortalContent, 'expand')
  def expand(self, applied_rule, **kw):
    """Expands the current movement downward.
    """
    return Rule._expand(self, applied_rule, **kw)
