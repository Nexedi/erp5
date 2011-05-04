# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2002, 2004 Nexedi SARL and Contributors. All Rights Reserved.
#                    Jean-Paul Smets-Solanes <jp@nexedi.com>
#                    Romain Courteaud <romain@nexedi.com>
# Copyright (c) 2010 Nexedi SA and Contributors. All Rights Reserved.
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
from Products.ERP5Type import Permissions, PropertySheet, interfaces
from Products.ERP5.Document.AmountGeneratorLine import AmountGeneratorLine


class TransformedResource(AmountGeneratorLine):
    """
    TransformedResource defines which resource is being transformed
    in order to produce a product define in the parent Transformation
    document.

    TODO:
    - transformations used to work perfectly for more than 3 dimensions
      of variations. However, this feature was broken with time and
      is no longer usable. It is time to reimplement it. This is
      completely unrelated to MatrixBox reimplementation unlike
      what is stated in some comments.
    """

    meta_type = 'ERP5 Transformed Resource'
    portal_type = 'Transformed Resource'

    # Declarative security
    security = ClassSecurityInfo()
    security.declareObjectProtected(Permissions.AccessContentsInformation)

    # Declarative properties
    property_sheets = (PropertySheet.TransformedResource, )

    ### Mapped Value Definition
    # Provide default mapped value properties and categories if
    # not defined
    def getMappedValuePropertyList(self):
      result = self._baseGetMappedValuePropertyList()
      if not result:
        # Since MappedValue does not inherit Amount, and type class of
        # Transformation {Operation,Transformed Resource} Cell
        # was changed to TransformedResource as a workaround,
        # we also need to check if 'self' has a quantity.
        # Otherwise, generated amounts could have 0 quantity
        # (overridden by cells that only define variation).
        result = ['quantity']
        # Take into account variation_property_list for each variation
        # for which hasProperty is true...
        # FIXME: Why the resource and not the model line itself ? Or both ??
        resource = self.getDefaultResourceValue()
        if resource is not None:
          result += resource.getVariationPropertyList()
        result = filter(self.hasProperty, result)
      return result

    def getMappedValueBaseCategoryList(self):
      result = list(self._baseGetMappedValueBaseCategoryList())
      if not result:
        if not self.hasCellContent(base_id='variation'):
          result = list(self.getVariationRangeBaseCategoryList()) # The current resource variation
        if 'trade_phase' not in result:
          result.append('trade_phase')
      return result

    def getCellAggregateKey(self):
      """Define a key in order to aggregate amounts at cell level"""
      return None

    @classmethod
    def getBaseAmountQuantity(cls, delivery_amount, base_application, rounding):
      value = delivery_amount.getGeneratedAmountQuantity(base_application)
      if base_application == 'base_amount/produced_quantity':
        value += delivery_amount.getConvertedQuantity()
      return value

    def getBaseApplication(self):
      """
      """
      return self.getBaseApplicationList()[0]

    def getBaseApplicationList(self):
      """
      """
      # It is OK to try to acquire
      return self._categoryGetBaseApplicationList() \
          or ['base_amount/produced_quantity']

    ### Variation matrix definition
    # XXX-JPS Some explanation needed
    security.declareProtected(Permissions.AccessContentsInformation,
                              'updateVariationCategoryList')
    def updateVariationCategoryList(self):
      """
        Check if variation category list of the resource changed and
        update transformed resource by doing a set cell range
      """
      self.setQVariationBaseCategoryList(self.getQVariationBaseCategoryList())
      self.setVVariationBaseCategoryList(self.getVVariationBaseCategoryList())

    security.declareProtected(Permissions.ModifyPortalContent,
                              '_setQVariationBaseCategoryList')
    def _setQVariationBaseCategoryList(self, value):
      """
        Defines the possible base categories which Quantity value (Q)
        variate on
      """
      self._baseSetQVariationBaseCategoryList(value)
      self._updateCellRange('quantity')

    security.declareProtected(Permissions.ModifyPortalContent,
                              '_setVVariationBaseCategoryList')
    def _setVVariationBaseCategoryList(self, value):
      """
        Defines the possible base categories which Variation value (V)
        variate on
      """
      self._baseSetVVariationBaseCategoryList(value)
      # XXX calling updatecellRange is better
      self._updateCellRange('variation')
      # XXX-JPS This should be handled by interaction workflow or interactor
      # XXX-JPS SO many cases are not handled well...

    security.declareProtected(Permissions.ModifyPortalContent,
                              'setVVariationBaseCategoryList')
    def setVVariationBaseCategoryList(self, value):
      """
        Defines the possible base categories which Variation value (V)
        variate on and reindex the object
      """
      self._setVVariationBaseCategoryList(value)
      self.reindexObject()
