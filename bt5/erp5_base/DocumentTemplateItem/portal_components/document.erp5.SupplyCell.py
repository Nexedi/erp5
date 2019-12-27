
##############################################################################
#
# Copyright (c) 2002 Nexedi SARL and Contributors. All Rights Reserved.
#                    Jean-Paul Smets-Solanes <jp@nexedi.com>
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

from Products.ERP5Type import Permissions, PropertySheet
from Products.ERP5.Document.Path import Path

class SupplyCell(Path):
  """A Supply Cell is used for different variations in a supply line.
  """

  meta_type = 'ERP5 Supply Cell'
  portal_type = 'Supply Cell'
  add_permission = Permissions.AddPortalContent

  # Declarative security
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  # Declarative properties
  property_sheets = ( PropertySheet.Base
                    , PropertySheet.CategoryCore
                    , PropertySheet.Amount
                    , PropertySheet.Task
                    , PropertySheet.Movement
                    , PropertySheet.Price
                    , PropertySheet.SupplyLine
                    , PropertySheet.Discount
                    , PropertySheet.Path
                    , PropertySheet.FlowCapacity
                    , PropertySheet.Predicate
                    , PropertySheet.MappedValue
                    , PropertySheet.Reference
                    )

  security.declareProtected( Permissions.AccessContentsInformation,
                             'hasCellContent' )
  def hasCellContent(self, base_id='movement'):
    """A cell cannot have cell content itself.
    """
    return 0

  # Override getQuantityUnitXXX to negate same methods defined in
  # Amount class. Because cell must acquire quantity unit from line
  # not from resource.
  security.declareProtected( Permissions.AccessContentsInformation,
                             'getQuantityUnitValue')
  def getQuantityUnitValue(self):
    return self.getParentValue().getQuantityUnitValue()

  security.declareProtected( Permissions.AccessContentsInformation,
                             'getQuantityUnit')
  def getQuantityUnit(self, checked_permission=None):
    return self.getParentValue().getQuantityUnit(checked_permission=checked_permission)
