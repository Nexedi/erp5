##############################################################################
#
# Copyright (c) 2002 Coramy SAS and Contributors. All Rights Reserved.
#                    Thierry_Faucher <Thierry_Faucher@coramy.com>
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

from Globals import InitializeClass, PersistentMapping
from AccessControl import ClassSecurityInfo

from Products.ERP5Type import Permissions, PropertySheet, Constraint, Interface
from Products.ERP5Type.XMLObject import XMLObject
from Products.ERP5Type.XMLMatrix import XMLMatrix
from Products.ERP5.Document.Domain import Domain

from zLOG import LOG

class GrilleConsommation(XMLObject, XMLMatrix):
    """
      A matrix which provides default quantities
      for a given quantity
    """

    meta_type = 'CORAMY Grille Consommation'
    portal_type = 'Grille Consommation'
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
                      , PropertySheet.VariationRange
                      , PropertySheet.GrilleConsommation
                      )

    # Factory Type Information
    factory_type_information = \
      {    'id'             : portal_type
         , 'meta_type'      : meta_type
         , 'description'    : """\
une gamme..."""
         , 'icon'           : 'grille_consommation_icon.gif'
         , 'product'        : 'Coramy'
         , 'factory'        : 'addGrilleConsommation'
         , 'immediate_view' : 'grille_consommation_view'
         , 'allow_discussion'     : 1
         , 'allowed_content_types': ('Variante Gamme',
                                      )
         , 'filter_content_types' : 1
         , 'global_allow'   : 1
         , 'actions'        :
        ( { 'id'            : 'view'
          , 'name'          : 'View'
          , 'category'      : 'object_view'
          , 'action'        : 'grille_consommation_view'
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
          , 'action'        : 'grille_consommation_print'
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

    security.declareProtected(Permissions.ModifyPortalContent, '_setTailleList')
    def _setTailleList(self, value):
      if type(value) is type('a'): value = [value]
      self._setCellRange(value, value, base_id='quantity')
      self._categorySetTaille(value)

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

    # Inheritance solving
    security.declareProtected(Permissions.ModifyPortalContent, 'checkConsistency')
    checkConsistency = XMLMatrix.checkConsistency

