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

from Globals import InitializeClass, PersistentMapping
from AccessControl import ClassSecurityInfo

from Products.CMFCore.WorkflowCore import WorkflowAction
from Products.ERP5Type import Permissions, PropertySheet, Constraint, Interface
from Products.ERP5Type.XMLMatrix import XMLMatrix
from Products.ERP5.Document.Container import Container as ERP5Container

from zLOG import LOG

class Container(ERP5Container):
    """
      Container is equivalent to a movement with qty 1.0 and resource = to the kind of packaging
      Container may point to item (ex. Container serial No or Parcel Serial No if tracing required)
      Container may eventually usa optional property sheet to store parcel No information (we use
      Item property sheet for that). Some acquisition may be required...

      Container Line / Container Cell is used to store quantities (never accounted)
      Container Line / Countainer Cell may point to Item
    """

    meta_type = 'CORAMY Container'
    portal_type = 'Container'
    add_permission = Permissions.AddPortalContent
    isPortalContent = 1
    isRADContent = 1

    # Declarative security
    security = ClassSecurityInfo()
    security.declareObjectProtected(Permissions.View)

    # Declarative interfaces
    __implements__ = ( Interface.Variated, )

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
                      , PropertySheet.Item
                      , PropertySheet.Container
                      , PropertySheet.SortIndex
                      )

    # Factory Type Information
    factory_type_information = \
      {    'id'             : portal_type
         , 'meta_type'      : meta_type
         , 'description'    : """\
Un container (colis, caisse,...)."""
         , 'icon'           : 'container_icon.gif'
         , 'product'        : 'Coramy'
         , 'factory'        : 'addContainer'
         , 'immediate_view' : 'container_view'
         , 'allow_discussion'     : 1
         , 'allowed_content_types': ('Container','Container Line',
                                      )
         , 'filter_content_types' : 1
         , 'global_allow'   : 1
         , 'actions'        :
        ( { 'id'            : 'view'
          , 'name'          : 'View'
          , 'category'      : 'object_view'
          , 'action'        : 'container_view'
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
          , 'action'        : 'container_print'
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
    security.declareProtected(Permissions.AccessContentsInformation, 'getTargetTotalQuantity')
    def getTargetTotalQuantity(self):
      """
        Returns the quantity if no cell or the total quantity if cells
      """
      aggregate = self.Container_zGetTotal()[0]
      return aggregate.target_total_quantity
