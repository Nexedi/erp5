##############################################################################
#    Copyright (C) 2001  MMmanager.org
#
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program; if not, write to the Free Software
#    Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
##############################################################################
"""
"""

ADD_CONTENT_PERMISSION = 'Add portal content'

from AccessControl import ClassSecurityInfo

from Products.ERP5Type import Permissions, PropertySheet, Constraint, Interface
from Products.ERP5Shop.Document.ShopProduct import ShopProduct
from Products.Base18.Document import Document18

import zLOG

class NetworkProduct( ShopProduct, Document18 ):
    """
        A Network Infrastructure Product used
        by nexedi.net
    """

    meta_type='Nexedi Service Product'
    portal_type='Service Product'
    effective_date = expiration_date = None
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
                      , PropertySheet.Document
                      , PropertySheet.Price
                      , PropertySheet.Resource
                      , PropertySheet.NetworkProduct
                      , PropertySheet.ShopProduct
                      )

    # Factory Type Information
    factory_type_information = \
      {    'id'             : portal_type
         , 'meta_type'      : meta_type
         , 'description'    : """\
A Network Product for nexedi.net services"""
         , 'icon'           : 'file_icon.gif'
         , 'product'        : 'Nexedi'
         , 'factory'        : 'addNetworkProduct'
         , 'immediate_view' : 'network_product_edit_form'
         , 'allow_discussion'     : 1
         , 'allowed_content_types': ('Variante Gamme',
                                      )
         , 'filter_content_types' : 1
         , 'global_allow'   : 1
         , 'actions'        :
        ( { 'id'            : 'view'
          , 'name'          : 'View'
          , 'category'      : 'object_view'
          , 'action'        : 'network_product_view'
          , 'permissions'   : (
              Permissions.View, )
          }
        , { 'id'            : 'edit'
          , 'name'          : 'Edit'
          , 'category'      : 'object_view'
          , 'action'        : 'network_product_edit_form'
          , 'permissions'   : (
              Permissions.ModifyPortalContent, )
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
          , 'action'        : 'document18_print'
          , 'permissions'   : (
              Permissions.View, )
          }
        , { 'id'            : 'metadata'
          , 'name'          : 'Metadata'
          , 'category'      : 'object_edit'
          , 'action'        : 'metadata_edit_form'
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

    def _getPrice(self, context):
        """
          Private price depending in the context
        """
        base_price = self.destination_base_price
        additional_price = 0.0
        for v in self.objectValues('Nexedi Service Pricing'):
          if v.test(context):
            if getattr(v, 'destination_base_price', None) is not None:
              base_price = v.destination_base_price
            if getattr(v, 'destination_additional_price', None) is not None:
              additional_price += v.destination_additional_price
        return base_price + additional_price
