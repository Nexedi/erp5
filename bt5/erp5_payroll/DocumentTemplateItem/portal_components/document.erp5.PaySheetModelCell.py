# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2010 Nexedi SA and Contributors. All Rights Reserved.
#                    Aurelien Calonne <aurel@nexedi.com>
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
from Products.ERP5Type import Permissions
from Products.ERP5.Document.TradeModelCell import TradeModelCell
from Products.ERP5Type.Core.Predicate import Predicate

class PaySheetModelCell(TradeModelCell):
  """Trade Model Line
  """
  meta_type = 'ERP5 Pay Sheet Model Cell'
  portal_type = 'Pay Sheet Model Cell'
  isCell = 1

  # Declarative security
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  def getMappedValueBaseCategoryList(self):
    result = self._baseGetMappedValueBaseCategoryList()
    if not result:
      if not self.hasCellContent(base_id='variation'):
        result = self.getVariationRangeBaseCategoryList() # The current resource variation
    return list(result) + ['trade_phase', 'quantity_unit']

  # Redefine some methods as we do not want to turn cells into predicate
  def edit(self, **kw):
    return super(Predicate, self).edit(**kw) # pylint: disable=bad-super-call

  def setPredicateCategoryList(self, *args, **kw):
    pass
