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
from Products.ERP5Type.Accessor.Constant import PropertyGetter as ConstantGetter
from Products.ERP5.Document.Delivery import Delivery

class NoIndexStockInventory(Delivery):
  """
  NoIndexStockInventory
  """
  # CMF Type Definition
  meta_type = 'ERP5 NoIndexStockInventory'
  portal_type = 'NoIndexStockInventory'
  isInventory = ConstantGetter('isInventory', value=True)

  # Declarative security
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  # Default Properties
  property_sheets = ( PropertySheet.Base
                    , PropertySheet.XMLObject
                    , PropertySheet.CategoryCore
                    , PropertySheet.DublinCore
                    , PropertySheet.Task
                    , PropertySheet.Arrow
                    , PropertySheet.Movement
                    , PropertySheet.Delivery
                    , PropertySheet.Path
                    , PropertySheet.FlowCapacity
                    , PropertySheet.Inventory
                    )

  security.declarePublic('alternateReindexObject')
  def alternateReindexObject(self, **kw):
    """
    This method is called when an inventory object is included in a
    group of catalogged objects.
    """
    return self.immediateReindexObject(**kw)

  # method used to build category list that willbe set on tmp line
  def appendToCategoryListFromUid(self, category_list, uid, base_category):
    object_list = [x.getObject() for x in self.portal_catalog(uid=uid)]
    if len(object_list):
      category_list.append("%s/%s" %(base_category, object_list[0].getRelativeUrl()))

  def appendToCategoryList(self, category_list, value, base_category):
    category_list.append("%s/%s" %(base_category, value))

  def splitAndExtendToCategoryList(self, category_list, value, *args, **kw):
    if value is not None:
      value_list = value.split('\n')
    else:
      value_list = []
    category_list.extend(value_list)

