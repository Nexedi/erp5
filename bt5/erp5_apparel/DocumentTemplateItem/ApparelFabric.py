##############################################################################
#
# Copyright (c) 2002-2009 Nexedi SA and Contributors. All Rights Reserved.
#                    Jean-Paul Smets-Solanes <jp@nexedi.com>
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

from Products.ERP5.Document.Resource import Resource
from Products.ERP5Type import Permissions, PropertySheet, Constraint, Interface
from Products.ERP5Type.Utils import rejectIn

class ApparelFabric(Resource):
    """
      A apparel fabric
    """

    meta_type = 'ERP5 Apparel Fabric'
    portal_type = 'Apparel Fabric'

    # Declarative security
    security = ClassSecurityInfo()
    security.declareObjectProtected(Permissions.AccessContentsInformation)

    # Declarative properties
    property_sheets = ( PropertySheet.Base
                      , PropertySheet.ApparelFabric
                      , PropertySheet.XMLObject
                      , PropertySheet.CategoryCore
                      , PropertySheet.DublinCore
                      , PropertySheet.Comment
                      , PropertySheet.Price
                      , PropertySheet.Resource
                      , PropertySheet.Reference
                      , PropertySheet.ApparelCollection
                      , PropertySheet.ApparelLabel
                      , PropertySheet.VariationRange
                      )



    # Unit conversion
    security.declareProtected(Permissions.AccessContentsInformation, 'convertQuantity')
    def convertQuantity(self, quantity, from_unit, to_unit):
      # XXX if from_unit == 'Surface/Centimetre_carre' and to_unit == 'Longueur/Metre':
      if from_unit == 'area/square centimeters' and to_unit == 'measurement/meter':
        # XXX return quantity / 100.0 / float(self.getLaizeUtile())
#        return quantity / 100.0 / float(self.getLaizeUtile())
        return quantity / 100.0 / float(self.getNetWidth())
      else:
        return quantity

    # Unit list
    security.declareProtected(Permissions.AccessContentsInformation, 'getQuantityUnitList')
    def getQuantityUnitList(self):
      my_default_quantity = self.getCategoryDefaultMembership('quantity_unit')
      # XXX return [my_default_quantity] + rejectIn( ['Surface/Centimetre_carre', 'Longueur/Metre'],
      return [my_default_quantity] + rejectIn( ['area/square centimeters', 'measurement/meter'],
                [my_default_quantity])
