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
from Products.CMFCore.WorkflowCore import WorkflowMethod
from Products.ERP5.Document.Resource import Resource
from Products.ERP5.Document.Order import Order as ERP5Order
from Products.ERP5Type import Permissions, PropertySheet, Constraint, Interface
from Products.ERP5.ERP5Globals import movement_type_list, default_section_category
from Products.CMFCore.WorkflowCore import WorkflowMethod

from zLOG import LOG

class ProductionOrder(ERP5Order):
    """
      Un ordre de fabrication....

    """

    meta_type = 'CORAMY Production Order'
    portal_type = 'Production Order'
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
                      , PropertySheet.Task
                      , PropertySheet.Arrow
                      , PropertySheet.TradeCondition
                      , PropertySheet.PaymentCondition
                      , PropertySheet.Comment
                      , PropertySheet.Reference
                      , PropertySheet.CoramyOrder
                      )

    # Factory Type Information
    factory_type_information = \
      {    'id'             : portal_type
         , 'meta_type'      : meta_type
         , 'description'    : """\
un ordre de fabrication..."""
         , 'icon'           : 'production_order_icon.gif'
         , 'product'        : 'Coramy'
         , 'factory'        : 'addProductionOrder'
         , 'immediate_view' : 'production_order_view'
         , 'allow_discussion'     : 1
         , 'allowed_content_types': ('Movement', 'Production Order Line',
                                      )
         , 'filter_content_types' : 1
         , 'global_allow'   : 1
         , 'actions'        :
        ( { 'id'            : 'view'
          , 'name'          : 'View'
          , 'category'      : 'object_view'
          , 'action'        : 'production_order_view'
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
          , 'action'        : 'production_order_print'
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

    security.declareProtected(Permissions.AccessContentsInformation, 'getFutureInventoryList')
    def getFutureInventoryList(self, section = None, node = None,
             node_category=None, section_category=default_section_category, simulation_state=None,
             ignore_variation=0, **kw):
      """
        Returns list of future inventory grouped by section or site
      """
      return self.getInventoryList(at_date=None, section=section, node=self.getDestination(),
                             node_category=node_category, section_category=section_category, **kw)
