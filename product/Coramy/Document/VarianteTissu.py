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

from Products.ERP5Type import Permissions, PropertySheet, Constraint, Interface
from Products.ERP5.Document.Variation import Variation
from Products.ERP5.Document.Image import Image

class VarianteTissu(Image, Variation):
    """
      Une variante tissu Coramy....
    """

    meta_type = 'CORAMY Variante Tissu'
    portal_type = 'Variante Tissu'
    add_permission = Permissions.AddPortalContent
    isPortalContent = 1
    isRADContent = 1

    # Declarative security
    security = ClassSecurityInfo()
    security.declareObjectProtected(Permissions.View)

    # Declarative properties
    property_sheets = ( PropertySheet.Base
                      , PropertySheet.CategoryCore
                      , PropertySheet.DublinCore
                      , PropertySheet.Resource
                      , PropertySheet.Reference
                      , PropertySheet.Price
                      , PropertySheet.Variation
                      , PropertySheet.VarianteTissu
                      )

    # Hard Wired Variation List
    # XXX - may be incompatible with future versions of ERP5
    variation_base_category_list = ('coloris', )

    # Factory Type Information
    factory_type_information = \
      {    'id'             : portal_type
         , 'meta_type'      : meta_type
         , 'description'    : """\
Une variante de tissu est une image d'un tissu particulier qui 
définit la couleur et les motifs de cette variante."""
         , 'icon'           : 'variante_tissu_icon.gif'
         , 'product'        : 'Coramy'
         , 'factory'        : 'addVarianteTissu'
         , 'immediate_view' : 'variante_modele_view'
         , 'actions'        :
        ( { 'id'            : 'view'
          , 'name'          : 'View'
          , 'category'      : 'object_view'
          , 'action'        : 'variante_tissu_view'
          , 'permissions'   : (
              Permissions.View, )
          }
        , { 'id'            : 'print'
          , 'name'          : 'Print'
          , 'category'      : 'object_print'
          , 'action'        : 'variante_tissu_print'
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


