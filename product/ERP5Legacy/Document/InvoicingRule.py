##############################################################################
#
# Copyright (c) 2002-2005 Nexedi SA and Contributors. All Rights Reserved.
#                    Sebastien Robin <seb@nexedi.com>
#                    Romain Courteaud <romain@nexedi.com>
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
# Foundation, Inc., 51 Franklin Street - Fifth Floor, Boston, MA 02110-1301,
# USA.
#
##############################################################################

from AccessControl import ClassSecurityInfo
from Products.ERP5Type import Permissions, PropertySheet, interfaces
from Products.ERP5Legacy.Document.Rule import Rule
from zLOG import LOG, WARNING

class InvoicingRule(Rule):
  """
    Invoicing Rule expand simulation created by a order or delivery rule.
  """

  # CMF Type Definition
  meta_type = 'ERP5 Invoicing Rule'
  portal_type = 'Invoicing Rule'
  add_permission = Permissions.AddPortalContent

  # Declarative security
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  security.declareProtected(Permissions.AccessContentsInformation,
                            'isAccountable')
  def isAccountable(self, movement):
    """
    Tells whether generated movement needs to be accounted or not.

    Invoice movement are never accountable, so simulation movement for
    invoice movements should not be accountable either.
    """
    return 0

  security.declareProtected(Permissions.ModifyPortalContent, 'expand')
  def expand(self, applied_rule, force=0, **kw):
    """
    Expands the rule:
    - generate a list of previsions
    - compare the prevision with existing children
      - get the list of existing movements (immutable, mutable, deletable)
      - compute the difference between prevision and existing (add,
        modify, remove)
    - add/modify/remove child movements to match prevision
    """
    return Rule._expand(self, applied_rule, force=force, **kw)

  def isDeliverable(self, movement):
    return movement.getResource() is not None

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getExpandablePropertyList')
  def getExpandablePropertyList(self, default=None):
    """
    Return a list of properties used in expand.
    """
    property_list = self._baseGetExpandablePropertyList()
    # For backward compatibility, we keep for some time the list
    # of hardcoded properties. Theses properties should now be
    # defined on the rule itself
    if len(property_list) == 0:
      LOG("Invoicing Rule , getExpandablePropertyList", WARNING,
                 "Hardcoded properties set, please define your rule correctly")
      property_list = (
        'aggregate_list',
        'base_contribution_list',
        'delivery_mode',
        'description',
        'destination_account',
        'destination_administration',
        'destination_decision',
        'destination_function',
        'destination_list',
        'destination_payment',
        'destination_project',
        'destination_section',
        'efficiency',
        'incoterm',
        'price',
        'price_currency',
        'quantity',
        'quantity_unit',
        'resource',
        'source',
        'source_account',
        'source_administration',
        'source_decision',
        'source_function',
        'source_payment',
        'source_project',
        'source_section',
        'start_date',
        'stop_date',
        'variation_category_list',
        'variation_property_dict',
      )
    return property_list
