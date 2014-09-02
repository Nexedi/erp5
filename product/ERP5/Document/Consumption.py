##############################################################################
#
# Copyright (c) 2002 Coramy SAS and Contributors. All Rights Reserved.
#                    Thierry_Faucher <Thierry_Faucher@coramy.com>
# Copyright (c) 2004 Nexedi SARL and Contributors. All Rights Reserved.
#                    Courteaud_Romain <romain@nexedi.com>
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
from Products.ERP5Type.XMLObject import XMLObject
from Products.ERP5Type.XMLMatrix import XMLMatrix
from Products.ERP5.mixin.variated import VariatedMixin


class Consumption(XMLObject, XMLMatrix, VariatedMixin):
    """
      A matrix which provides default quantities
      for a given quantity
    """

    meta_type = 'ERP5 Consumption'
    portal_type = 'Consumption'

    # Declarative security
    security = ClassSecurityInfo()
    security.declareObjectProtected(Permissions.AccessContentsInformation)

    # Declarative properties
    property_sheets = ( PropertySheet.Base
                      , PropertySheet.XMLObject
                      , PropertySheet.CategoryCore
                      , PropertySheet.DublinCore
                      , PropertySheet.VariationRange
                      )

    security.declareProtected(Permissions.ModifyPortalContent,
                              '_setVariationCategoryList')
    def _setVariationCategoryList(self,value):
      """
        Set consumption variation category list.
        Set matrix cell range.
      """
      self._setCategoryMembership(self.getVariationRangeBaseCategoryList(),
                                  value, base=1)
      # XXX Must use in futur this method, but it failed today
      #VariatedMixin._setVariationCategoryList(self, value)
      # XXX FIXME: Use a interaction workflow instead
      # Kept for compatibility.
      self.updateCellRange(base_id='quantity')

    security.declareProtected(Permissions.ModifyPortalContent,
                              'setVariationCategoryList')
    def setVariationCategoryList(self,value):
      """
        Set consumption variation category list.
        Reindex Object.
      """
      self._setVariationCategoryList(value)
      self.reindexObject()

    security.declareProtected(Permissions.ModifyPortalContent,
                              'getVariationRangeBaseCategoryItemList')
    def getVariationRangeBaseCategoryItemList(self):
      """
        Return range of base variation item
        Left display
      """
      # XXX get TitleOrId
      return map( lambda x: (x,x)  , self.getVariationRangeBaseCategoryList() )

    security.declareProtected(Permissions.ModifyPortalContent,
                              'getQuantityRatio')
    def getQuantityRatio(self, variation_category_line,
                         variation_category_column):
      """
        Return quantity ratio for a virtual cell.
        Return None if not result can be return.
      """
      cell_quantity_ratio_list = []

      for variation_category in (variation_category_line,
                                 variation_category_column):
        cell = self.getCell(variation_category, base_id='quantity')
        if cell is None:
          return None
        else:
          cell_quantity_ratio = cell.getProperty('quantity')
          if cell_quantity_ratio in [None, 0, '']:
            return None
          else:
            cell_quantity_ratio_list.append( cell_quantity_ratio )

      return cell_quantity_ratio_list[1] / cell_quantity_ratio_list[0]
