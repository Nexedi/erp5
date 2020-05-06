##############################################################################
#
# Copyright (c) 2008 Nexedi SA and Contributors. All Rights Reserved.
#                    Jerome Perrin <jerome@nexedi.com>
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

from Products.ERP5.Document.DeliveryLine import DeliveryLine


class TaxLine(DeliveryLine):
    """ Tax Line
    """
    meta_type = 'ERP5 Tax Line'
    portal_type = 'Tax Line'

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
                      , PropertySheet.ItemAggregation
                      , PropertySheet.Reference
                      , PropertySheet.SortIndex
                      )

    security.declareProtected(Permissions.AccessContentsInformation,
                              'isAccountable')
    def isAccountable(self):
      """Return true if the parent is accountable and
      not an accounting transaction.

      NOTE: this is because, if the parent is an accounting transaction,
      the accounting is done with another accounting transaction line,
      so making tax lines accountable would duplicate the accounting.
      """
      delivery = self.getParentValue()
      if delivery.isAccountable():
        portal = delivery.getPortalObject()
        type_list = portal.getPortalAccountingTransactionTypeList()
        return delivery.getPortalType() not in type_list
      return 0

    security.declareProtected(Permissions.AccessContentsInformation,
                              'hasCellContent')
    def hasCellContent(self, base_id='movement'):
      """Tax line does not contain cell
      """
      return 0

    security.declareProtected(Permissions.AccessContentsInformation,
                              'isMovement' )
    def isMovement(self):
      """Tax lines are movements
      """
      return 1

