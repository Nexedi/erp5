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

from Products.ERP5.Document.Resource import Resource
from Products.ERP5Type import Permissions, PropertySheet, Constraint, Interface
from Products.ERP5Type.Utils import rejectIn

class Tissu(Resource):
    """
      Un tissu Coramy....
    """

    meta_type = 'CORAMY Tissu'
    portal_type = 'Tissu'
    add_permission = Permissions.AddPortalContent
    isPortalContent = 1
    isRADContent = 1

    # Declarative security
    security = ClassSecurityInfo()
    security.declareObjectProtected(Permissions.View)

    # Declarative properties
    property_sheets = ( PropertySheet.Base
                      , PropertySheet.XMLObject
                      , PropertySheet.CategoryCore
                      , PropertySheet.DublinCore
                      , PropertySheet.Price
                      , PropertySheet.Resource
                      , PropertySheet.Reference
                      , PropertySheet.Tissu
                      )

    # Hard Wired Variation List
    # XXX - may be incompatible with future versions of ERP5
    variation_base_category_list = ('coloris', )

    # Factory Type Information
    factory_type_information = \
      {    'id'             : portal_type
         , 'meta_type'      : meta_type
         , 'description'    : """\
Un tissu est une resource variantable en couleur."""
         , 'icon'           : 'tissu_icon.gif'
         , 'product'        : 'Coramy'
         , 'factory'        : 'addTissu'
         , 'immediate_view' : 'tissu_view'
         , 'allow_discussion'     : 1
         , 'allowed_content_types': ('Variante Tissu',
                                      )
         , 'filter_content_types' : 1
         , 'global_allow'   : 1
         , 'actions'        :
        ( { 'id'            : 'view'
          , 'name'          : 'View'
          , 'category'      : 'object_view'
          , 'action'        : 'tissu_view'
          , 'permissions'   : (
              Permissions.View, )
          }
        , { 'id'            : 'list'
          , 'name'          : 'Object Contents'
          , 'category'      : 'object_action'
          , 'action'        : 'folder_contents'
          , 'permissions'   : (
              Permissions.View, )
          }
        , { 'id'            : 'print'
          , 'name'          : 'Print'
          , 'category'      : 'object_print'
          , 'action'        : 'tissu_print'
          , 'permissions'   : (
              Permissions.View, )
          }
        , { 'id'            : 'metadata'
          , 'name'          : 'Metadata'
          , 'category'      : 'object_view'
          , 'action'        : 'metadata_edit'
          , 'permissions'   : (
              Permissions.View, )
          }
        , { 'id'            : 'translate'
          , 'name'          : 'Translate'
          , 'category'      : 'object_action'
          , 'action'        : 'translation_template_view'
          , 'permissions'   : (
              Permissions.TranslateContent, )
          }
        )
      }

    def _setTitle(self, value):
      """
        Here we see that we must define an notion
        of priority in the way fields are updated
      """
      if value != self.getTitle():
        self.title = value

    security.declareProtected(Permissions.View, 'getTitle')
    def getTitle(self):
      """
        Returns the title if it exists or a combination of
        first name and last name
      """
      if self.title == '':
        return self.getId()
      else:
        return self.title
    Title = getTitle

    security.declareProtected(Permissions.ModifyPortalContent, 'setTitle')
    def setTitle(self, value):
      """
        Updates the title if necessary
      """
      self._setTitle(value)
      self.reindexObject()

    # Unit conversion
    security.declareProtected(Permissions.AccessContentsInformation, 'convertQuantity')
    def convertQuantity(self, quantity, from_unit, to_unit):
      if from_unit == 'Surface/Centimetre_carre' and to_unit == 'Longueur/Metre':
        return quantity / 100.0 / float(self.getLaizeUtile())
      else:
        return quantity


    # Unit list
    security.declareProtected(Permissions.AccessContentsInformation, 'getQuantityUnitList')
    def getQuantityUnitList(self):
      my_default_quantity = self.getCategoryDefaultMembership('quantity_unit')
      return [my_default_quantity] + rejectIn( ['Surface/Centimetre_carre', 'Longueur/Metre'],
                [my_default_quantity])

                
