##############################################################################
#
# Copyright (c) 2005 Nexedi SARL and Contributors. All Rights Reserved.
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

from Products.ERP5.Document.Resource import Resource
from zope.interface import implements

class CashCurrency(Resource):
  """
    CashCurrency defines a cash model for a certain currency.
    Typically, banknotes and coins.
  """

  meta_type = 'ERP5Banking Cash Currency'
  portal_type = 'Cash Currency'
  add_permission = Permissions.AddPortalContent

  # Declarative security
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.View)

  # Declarative interfaces
  implements( interfaces.IVariated, )

  # Declarative properties
  property_sheets = ( PropertySheet.Base
                    , PropertySheet.XMLObject
                    , PropertySheet.CategoryCore
                    , PropertySheet.DublinCore
                    , PropertySheet.Price
                    , PropertySheet.Resource
                    , PropertySheet.Reference
                    , PropertySheet.FlowCapacity
                    , PropertySheet.VariationRange
                    , PropertySheet.CashCurrency
                    )

  security.declareProtected(Permissions.View, 'getTitle')
  def getTitle(self, **kw):
    """
      The title depends on the Portal Type and the value, for example :
        Piece de 500
    """
    former = getattr(self, 'former', 0)
    title = self.getPortalType()
    price = self.getBasePrice()
    if price is None:
      price = 'Not Defined'
    else:
      price = '%i' % int(price)
    if former:
      return 'Former %s of %s' % (title, price)
    else:
      return '%s of %s' % (title, price)

  security.declareProtected(Permissions.View, 'getTranslatedTitle')
  def getTranslatedTitle(self,**kw):
    """
      The title depends on the Portal Type and the value, for example :
        Piece de 500
    """
    former = getattr(self, 'former', 0)
    title = self.getTranslatedPortalType()
    price = self.getBasePrice()
    if price is None:
      price = 'Not Defined'
    else:
      price = '%i' % int(price)
    if former:
      return  self.Base_translateString('Former ${title} of ${value}', mapping = {'title' : str(title), 'value' : str(price)})
    else:
      return  self.Base_translateString('${title} of ${value}', mapping = {'title' : str(title), 'value' : str(price)})

  security.declareProtected(Permissions.ModifyPortalContent, '_setVariationList')
  def _setVariationList(self,value):
    """
      We will create cells by the same time
    """
    #LOG('_setVariationList, value',0,value)
    self._categorySetVariationList(value)
    self.setVariationBaseCategoryList(('cash_status','emission_letter','variation'))
    #all_variation_list = self.OrderLine_getMatrixItemList()
    #emission_letter_list = [x for x in all_variation_list if x.startswith('emission_letter')]
    emission_letter_list = [x[1] for x in self.portal_categories.emission_letter.getCategoryChildTitleItemList()[1:]]
    self._categorySetEmissionLetterList(emission_letter_list)
    #cash_status_list = [x for x in all_variation_list if x.startswith('cash_status')]
    cash_status_list = [x[1] for x in self.portal_categories.cash_status.getCategoryChildTitleItemList()[1:]]
    self._categorySetCashStatusList(cash_status_list)

  security.declareProtected(Permissions.ModifyPortalContent, 'setVariationList')
  def setVariationList(self,value):
    """
      Call the private method
    """
    self._setVariationList(value)

  # Cell Related
  security.declareProtected( Permissions.ModifyPortalContent, 'newCellContent' )
  def newCellContent(self, id):
    """
      This method can be overriden
    """
    self.invokeFactory(type_name="Set Mapped Value",id=id)
    return self.get(id)

