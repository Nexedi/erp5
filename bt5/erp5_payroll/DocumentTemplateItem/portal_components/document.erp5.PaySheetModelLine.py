##############################################################################
#
# Copyright (c) 2007-2009 Nexedi SA and Contributors. All Rights Reserved.
#                    Fabien Morin <fabien@nexedi.com>
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
from Products.ERP5.Document.TradeModelLine import TradeModelLine

class PaySheetModelLine(TradeModelLine):
  """
    A PaySheetModelLine object allows to implement lines in
    PaySheetModel.
    A PaySheetModelLine contain all parameters witch make it possible to
    calculate a service contribution.
  """
  edited_property_list = ['price', 'causality','resource','quantity',
              'title', 'base_application_list', 'base_contribution_list']

  meta_type = 'ERP5 Pay Sheet Model Line'
  portal_type = 'Pay Sheet Model Line'
  add_permission = Permissions.AddPortalContent

  # Declarative security
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  # Declarative properties
  property_sheets = ( PropertySheet.Base
                    , PropertySheet.XMLObject
                    , PropertySheet.CategoryCore
                    , PropertySheet.Amount
                    , PropertySheet.Task
                    , PropertySheet.Arrow
                    , PropertySheet.Movement
                    , PropertySheet.Price
                    , PropertySheet.VariationRange
                    , PropertySheet.MappedValue
                    , PropertySheet.TradeModelLine
                    , PropertySheet.Predicate
                    , PropertySheet.Reference
                    )

  security.declareProtected(Permissions.ModifyPortalContent,
                            'newCellContent' )
  def newCellContent(self, id, portal_type='Pay Sheet Model Cell', **kw):
    """Overriden to specify default portal type
    """
    return self.newContent(id=id, portal_type=portal_type, **kw)
