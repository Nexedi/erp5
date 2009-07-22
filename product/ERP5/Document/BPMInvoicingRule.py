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

#### Helper methods for expand
  def _getExpandablePropertyUpdateDict(self, applied_rule, movement, business_path,
      **kw):
    return {
      'deliverable': 1
    }

  def _getInputMovementList(self, applied_rule):
    """Returns list of input movements for applied rule"""
    return [applied_rule.getParentValue()]

  def isDeliverable(self, movement):
    return movement.getResource() is not None
