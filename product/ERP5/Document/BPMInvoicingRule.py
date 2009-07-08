# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2002-2009 Nexedi SA and Contributors. All Rights Reserved.
#                    Sebastien Robin <seb@nexedi.com>
#                    Romain Courteaud <romain@nexedi.com>
#                    Łukasz Nowak <luke@nexedi.com>
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
from Products.ERP5Type import Permissions, PropertySheet
from Products.ERP5.Document.BPMRule import BPMRule

class BPMInvoicingRule(BPMRule):
  """
    DISCLAIMER: Refer to BPMRule docstring disclaimer.

    This is BPM enabled Invoicing Rule
  """

  # CMF Type Definition
  meta_type = 'ERP5 BPM Invoicing Rule'
  portal_type = 'BPM Invoicing Rule'
  add_permission = Permissions.AddPortalContent
  isPortalContent = 1
  isRADContent = 1

  # Declarative security
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  # Default Properties
  property_sheets = ( PropertySheet.Base
                    , PropertySheet.XMLObject
                    , PropertySheet.CategoryCore
                    , PropertySheet.DublinCore
                    , PropertySheet.Task
                    , PropertySheet.AppliedRule
                    )

  security.declareProtected(Permissions.AccessContentsInformation,
                            'isAccountable')
  def isAccountable(self, movement):
    """
    Tells whether generated movement needs to be accounted or not.

    Invoice movement are never accountable, so simulation movement for
    invoice movements should not be accountable either.
    """
    return 0

#### Helper methods for expand
  def _generatePrevisionList(self, applied_rule, **kw):
    return_list = []
    for prevision_dict in BPMRule._generatePrevisionList(self, applied_rule,
        **kw):
      prevision_dict['deliverable'] = 1
      return_list.append(prevision_dict)
    return return_list

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
    parent_movement = applied_rule.getParentValue()
    if parent_movement is not None:
      if not parent_movement.isFrozen():
        add_list, modify_dict, \
          delete_list = self._getCompensatedMovementList(applied_rule, **kw)
        for movement_id in delete_list:
          applied_rule._delObject(movement_id)

        for movement, prop_dict in modify_dict.items():
          applied_rule[movement].edit(**prop_dict)

        for movement_dict in add_list:
          if 'id' in movement_dict.keys():
            mvmt_id = applied_rule._get_id(movement_dict.pop('id'))
            new_mvmt = applied_rule.newContent(id=mvmt_id,
                portal_type=self.movement_type)
          else:
            new_mvmt = applied_rule.newContent(portal_type=self.movement_type)
          new_mvmt.edit(**movement_dict)

    # Pass to base class
    BPMRule.expand(self, applied_rule, force=force, **kw)

  def isDeliverable(self, movement):
    return movement.getResource() is not None

