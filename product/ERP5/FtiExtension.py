##############################################################################
#
# Copyright (c) 2002 Nexedi SARL and Contributors. All Rights Reserved.
#                    Sebastien Robin <seb@nexedi.com>
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

"""
We will use this file in order to add fti

fti means factory type information, it is used in order to
create a portal type.

There's already many fti defined inside Document classes, but
here we will put fti for portal types based on a class already
existing. For example we can create the portal type "Product"
based on the class "Resource"
"""

from Products.ERP5Type import Permissions

#factory_type_information {}

factory_type_information = (
      {    'id'             : 'Product'
         , 'meta_type'      : 'ERP5 Resource'
         , 'title'          : 'Product'
         , 'description'    : """\
A Product object holds the information about
a manufactured product, like a pen, a bicycle..."""
         , 'icon'           : 'organisation_icon.gif'
         , 'product'        : 'ERP5'
         , 'factory'        : 'addResource'
         , 'immediate_view' : 'product_view'
         , 'actions'        :
        ( { 'id'            : 'view'
          , 'name'          : 'View'
          , 'category'      : 'object_view'
          , 'action'        : 'product_view'
          , 'permissions'   : (
              Permissions.View, )
          }
        , { 'id'            : 'print'
          , 'name'          : 'Print'
          , 'category'      : 'object_print'
          , 'action'        : 'resource_print'
          , 'permissions'   : (
              Permissions.View, )
          }
        , { 'id'            : 'metadata'
          , 'name'          : 'Metadata'
          , 'category'      : 'object_edit'
          , 'action'        : 'metadata_edit'
          , 'permissions'   : (
              Permissions.View, )
          }
        , { 'id'            : 'history'
          , 'name'          : 'History'
          , 'category'      : 'object_view'
          , 'action'        : 'history_view'
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
      },

      {    'id'             : 'Product Module'
         , 'meta_type'      : 'ERP5 Folder'
         , 'title'          : 'Product Module'
         , 'description'    : """\
An Order..."""
         , 'icon'           : 'folder_icon.gif'
         , 'product'        : 'ERP5Type'
         , 'factory'        : 'addFolder'
         , 'immediate_view' : 'folder_view'
         , 'allowed_content_types': ('Product',
                                      )

         , 'actions'        :
        ( { 'id'            : 'view'
          , 'name'          : 'View'
          , 'category'      : 'object_view'
          , 'action'        : 'product_list'
          , 'permissions'   : (
              Permissions.View, )
          }
        , { 'id'            : 'print'
          , 'name'          : 'Print'
          , 'category'      : 'object_print'
          , 'action'        : 'resource_print'
          , 'permissions'   : (
              Permissions.View, )
          }
        , { 'id'            : 'metadata'
          , 'name'          : 'Metadata'
          , 'category'      : 'object_edit'
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
      },

      {    'id'             : 'Service'
         , 'meta_type'      : 'ERP5 Resource'
         , 'title'          : 'Service'
         , 'description'    : """\
A Product object holds the information about
a manufactured product, like a pen, a bicycle..."""
         , 'icon'           : 'organisation_icon.gif'
         , 'product'        : 'ERP5'
         , 'factory'        : 'addResource'
         , 'immediate_view' : 'service_view'
         , 'allowed_content_types': ('',
                                      )
         , 'actions'        :
        ( { 'id'            : 'view'
          , 'name'          : 'View'
          , 'category'      : 'object_view'
          , 'action'        : 'service_view'
          , 'permissions'   : (
              Permissions.View, )
          }
        , { 'id'            : 'print'
          , 'name'          : 'Print'
          , 'category'      : 'object_print'
          , 'action'        : 'resource_print'
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
        , { 'id'            : 'history'
          , 'name'          : 'History'
          , 'category'      : 'object_view'
          , 'action'        : 'history_view'
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
      },

      {    'id'             : 'Service Module'
         , 'meta_type'      : 'ERP5 Folder'
         , 'title'          : 'Service Module'
         , 'description'    : """\
An Order..."""
         , 'icon'           : 'folder_icon.gif'
         , 'product'        : 'ERP5Type'
         , 'factory'        : 'addFolder'
         , 'immediate_view' : 'folder_view'
         , 'allowed_content_types': ('Service',
                                      )
         , 'actions'        :
        ( { 'id'            : 'view'
          , 'name'          : 'View'
          , 'category'      : 'object_view'
          , 'action'        : 'service_list'
          , 'permissions'   : (
              Permissions.View, )
          }
        , { 'id'            : 'print'
          , 'name'          : 'Print'
          , 'category'      : 'object_print'
          , 'action'        : 'resource_print'
          , 'permissions'   : (
              Permissions.View, )
          }
        , { 'id'            : 'metadata'
          , 'name'          : 'Metadata'
          , 'category'      : 'object_edit'
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
      },

      {    'id'             : 'Purchase Packing List'
         , 'meta_type'      : 'ERP5 Purchase Packing List'
         , 'title'          : 'Purchase Packing List'
         , 'description'    : """\
A Product object holds the information about
a manufactured product, like a pen, a bicycle..."""
         , 'icon'           : 'organisation_icon.gif'
         , 'product'        : 'ERP5'
         , 'factory'        : 'addPackingList'
         , 'immediate_view' : 'purchase_packing_list_view'
         , 'allowed_content_types': ('Purchase Packing List Line',
                      )
         , 'actions'        :
        ( { 'id'            : 'view'
          , 'name'          : 'View'
          , 'category'      : 'object_view'
          , 'action'        : 'purchase_packing_list_view'
          , 'permissions'   : (
              Permissions.View, )
          }
        , { 'id'            : 'print'
          , 'name'          : 'Print'
          , 'category'      : 'object_print'
          , 'action'        : 'resource_print'
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
        , { 'id'            : 'history'
          , 'name'          : 'History'
          , 'category'      : 'object_view'
          , 'action'        : 'history_view'
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
      },

      {    'id'             : 'Purchase Packing List Line'
         , 'meta_type'      : 'ERP5 Purchase Packing List Line'
         , 'title'          : 'Purchase Packing List Line'
         , 'description'    : """\
A Product object holds the information about
a manufactured product, like a pen, a bicycle..."""
         , 'icon'           : 'organisation_icon.gif'
         , 'product'        : 'ERP5'
         , 'factory'        : 'addDeliveryLine'
         , 'immediate_view' : 'purchase_packing_list_line_view'
         , 'actions'        :
        ( { 'id'            : 'view'
          , 'name'          : 'View'
          , 'category'      : 'object_view'
          , 'action'        : 'purchase_packing_list_line_view'
          , 'permissions'   : (
              Permissions.View, )
          }
        , { 'id'            : 'print'
          , 'name'          : 'Print'
          , 'category'      : 'object_print'
          , 'action'        : 'resource_print'
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
      },

      {    'id'             : 'Purchase Packing List Module'
         , 'meta_type'      : 'ERP5 Folder'
         , 'title'          : 'Purchase Packing List Module'
         , 'description'    : """\
An Order..."""
         , 'icon'           : 'folder_icon.gif'
         , 'product'        : 'ERP5Type'
         , 'factory'        : 'addFolder'
         , 'immediate_view' : 'folder_view'
         , 'allowed_content_types': ('Internal Packing List',
                                      )
         , 'actions'        :
        ( { 'id'            : 'view'
          , 'name'          : 'View'
          , 'category'      : 'object_view'
          , 'action'        : 'purchase_packing_list_list'
          , 'permissions'   : (
              Permissions.View, )
          }
        , { 'id'            : 'print'
          , 'name'          : 'Print'
          , 'category'      : 'object_print'
          , 'action'        : 'resource_print'
          , 'permissions'   : (
              Permissions.View, )
          }
        , { 'id'            : 'metadata'
          , 'name'          : 'Metadata'
          , 'category'      : 'object_edit'
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
      },

      {    'id'             : 'Internal Packing List'
         , 'meta_type'      : 'ERP5 Internal Packing List'
         , 'title'          : 'Internal Packing List'
         , 'description'    : """\
A Product object holds the information about
a manufactured product, like a pen, a bicycle..."""
         , 'icon'           : 'organisation_icon.gif'
         , 'product'        : 'ERP5'
         , 'factory'        : 'addPackingList'
         , 'immediate_view' : 'internal_packing_list_view'
         , 'allowed_content_types': ('Internal Packing List Line',
                      )
         , 'actions'        :
        ( { 'id'            : 'view'
          , 'name'          : 'View'
          , 'category'      : 'object_view'
          , 'action'        : 'internal_packing_list_view'
          , 'permissions'   : (
              Permissions.View, )
          }
        , { 'id'            : 'print'
          , 'name'          : 'Print'
          , 'category'      : 'object_print'
          , 'action'        : 'resource_print'
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
        , { 'id'            : 'history'
          , 'name'          : 'History'
          , 'category'      : 'object_view'
          , 'action'        : 'history_view'
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
      },

      {    'id'             : 'Internal Packing List Line'
         , 'meta_type'      : 'ERP5 Internal Packing List Line'
         , 'title'          : 'Purchase Packing List Line'
         , 'description'    : """\
A Product object holds the information about
a manufactured product, like a pen, a bicycle..."""
         , 'icon'           : 'organisation_icon.gif'
         , 'product'        : 'ERP5'
         , 'factory'        : 'addDeliveryLine'
         , 'immediate_view' : 'internal_packing_list_line_view'
         , 'actions'        :
        ( { 'id'            : 'view'
          , 'name'          : 'View'
          , 'category'      : 'object_view'
          , 'action'        : 'internal_packing_list_line_view'
          , 'permissions'   : (
              Permissions.View, )
          }
        , { 'id'            : 'print'
          , 'name'          : 'Print'
          , 'category'      : 'object_print'
          , 'action'        : 'resource_print'
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
      },

      {    'id'             : 'Internal Packing List Module'
         , 'meta_type'      : 'ERP5 Folder'
         , 'title'          : 'Internal Packing List Module'
         , 'description'    : """\
An Order..."""
         , 'icon'           : 'folder_icon.gif'
         , 'product'        : 'ERP5Type'
         , 'factory'        : 'addFolder'
         , 'immediate_view' : 'folder_view'
         , 'allowed_content_types': ('Internal Packing List',
                                      )
         , 'actions'        :
        ( { 'id'            : 'view'
          , 'name'          : 'View'
          , 'category'      : 'object_view'
          , 'action'        : 'internal_packing_list_list'
          , 'permissions'   : (
              Permissions.View, )
          }
        , { 'id'            : 'print'
          , 'name'          : 'Print'
          , 'category'      : 'object_print'
          , 'action'        : 'resource_print'
          , 'permissions'   : (
              Permissions.View, )
          }
        , { 'id'            : 'metadata'
          , 'name'          : 'Metadata'
          , 'category'      : 'object_edit'
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
      },

      {    'id'             : 'Sale Packing List'
         , 'meta_type'      : 'ERP5 Sale Packing List'
         , 'title'          : 'Sale Packing List'
         , 'description'    : """\
A Product object holds the information about
a manufactured product, like a pen, a bicycle..."""
         , 'icon'           : 'organisation_icon.gif'
         , 'product'        : 'ERP5'
         , 'factory'        : 'addPackingList'
         , 'immediate_view' : 'sale_packing_list_view'
         , 'allowed_content_types': ('Sale Packing List Line',
                      )
         , 'actions'        :
        ( { 'id'            : 'view'
          , 'name'          : 'View'
          , 'category'      : 'object_view'
          , 'action'        : 'sale_packing_list_view'
          , 'permissions'   : (
              Permissions.View, )
          }
        , { 'id'            : 'print'
          , 'name'          : 'Print'
          , 'category'      : 'object_print'
          , 'action'        : 'resource_print'
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
        , { 'id'            : 'history'
          , 'name'          : 'History'
          , 'category'      : 'object_view'
          , 'action'        : 'history_view'
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
      },

      {    'id'             : 'Sale Packing List Line'
         , 'meta_type'      : 'ERP5 Sale Packing List Line'
         , 'title'          : 'Sale Packing List Line'
         , 'description'    : """\
A Product object holds the information about
a manufactured product, like a pen, a bicycle..."""
         , 'icon'           : 'organisation_icon.gif'
         , 'product'        : 'ERP5'
         , 'factory'        : 'addDeliveryLine'
         , 'immediate_view' : 'sale_packing_list_line_view'
         , 'actions'        :
        ( { 'id'            : 'view'
          , 'name'          : 'View'
          , 'category'      : 'object_view'
          , 'action'        : 'sale_packing_list_line_view'
          , 'permissions'   : (
              Permissions.View, )
          }
        , { 'id'            : 'print'
          , 'name'          : 'Print'
          , 'category'      : 'object_print'
          , 'action'        : 'resource_print'
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
      },

      {    'id'             : 'Sale Packing List Module'
         , 'meta_type'      : 'ERP5 Folder'
         , 'title'          : 'Sale Packing List Module'
         , 'description'    : """\
An Order..."""
         , 'icon'           : 'folder_icon.gif'
         , 'product'        : 'ERP5Type'
         , 'factory'        : 'addFolder'
         , 'immediate_view' : 'folder_view'
         , 'allowed_content_types': ('Sale Packing List',
                                      )
         , 'actions'        :
        ( { 'id'            : 'view'
          , 'name'          : 'View'
          , 'category'      : 'object_view'
          , 'action'        : 'sale_packing_list_list'
          , 'permissions'   : (
              Permissions.View, )
          }
        , { 'id'            : 'print'
          , 'name'          : 'Print'
          , 'category'      : 'object_print'
          , 'action'        : 'resource_print'
          , 'permissions'   : (
              Permissions.View, )
          }
        , { 'id'            : 'metadata'
          , 'name'          : 'Metadata'
          , 'category'      : 'object_edit'
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
      },

      {    'id'             : 'Purchase Order Line'
         , 'meta_type'      : 'ERP5 Purchase Order Line'
         , 'title'          : 'Purchase Order Line'
         , 'description'    : """\
A Product object holds the information about
a manufactured product, like a pen, a bicycle..."""
         , 'icon'           : 'organisation_icon.gif'
         , 'product'        : 'ERP5'
         , 'factory'        : 'addOrderLine'
         , 'immediate_view' : 'purchase_order_line_view'
         , 'actions'        :
        ( { 'id'            : 'view'
          , 'name'          : 'View'
          , 'category'      : 'object_view'
          , 'action'        : 'purchase_order_line_view'
          , 'permissions'   : (
              Permissions.View, )
          }
        , { 'id'            : 'print'
          , 'name'          : 'Print'
          , 'category'      : 'object_print'
          , 'action'        : 'resource_print'
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
      },

      {    'id'             : 'Sale Order Line'
         , 'meta_type'      : 'ERP5 Sale Order Line'
         , 'title'          : 'Sale Order Line'
         , 'description'    : """\
A Product object holds the information about
a manufactured product, like a pen, a bicycle..."""
         , 'icon'           : 'organisation_icon.gif'
         , 'product'        : 'ERP5'
         , 'factory'        : 'addOrderLine'
         , 'immediate_view' : 'sale_order_line_view'
         , 'actions'        :
        ( { 'id'            : 'view'
          , 'name'          : 'View'
          , 'category'      : 'object_view'
          , 'action'        : 'sale_order_line_view'
          , 'permissions'   : (
              Permissions.View, )
          }
        , { 'id'            : 'print'
          , 'name'          : 'Print'
          , 'category'      : 'object_print'
          , 'action'        : 'resource_print'
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
      },

      {    'id'             : 'Sale Order'
         , 'meta_type'      : 'ERP5 Sale Order'
         , 'title'          : 'Sale Order'
         , 'description'    : """\
An Order..."""
         , 'icon'           : 'organisation_icon.gif'
         , 'product'        : 'ERP5'
         , 'factory'        : 'addOrder'
         , 'immediate_view' : 'sale_order_view'
         , 'actions'        :
        ( { 'id'            : 'view'
          , 'name'          : 'View'
          , 'category'      : 'object_view'
          , 'action'        : 'sale_order_view'
          , 'permissions'   : (
              Permissions.View, )
          }
        , { 'id'            : 'print'
          , 'name'          : 'Print'
          , 'category'      : 'object_print'
          , 'action'        : 'resource_print'
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
        , { 'id'            : 'history'
          , 'name'          : 'History'
          , 'category'      : 'object_view'
          , 'action'        : 'history_view'
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
      },

      {    'id'             : 'Sale Order Module'
         , 'meta_type'      : 'ERP5 Folder'
         , 'title'          : 'Sale Order Module'
         , 'description'    : """\
An Order..."""
         , 'icon'           : 'folder_icon.gif'
         , 'product'        : 'ERP5Type'
         , 'factory'        : 'addFolder'
         , 'immediate_view' : 'folder_view'
         , 'allowed_content_types': ('Sale Order',
                                      )
         , 'actions'        :
        ( { 'id'            : 'view'
          , 'name'          : 'View'
          , 'category'      : 'object_view'
          , 'action'        : 'sale_order_list'
          , 'permissions'   : (
              Permissions.View, )
          }
        , { 'id'            : 'print'
          , 'name'          : 'Print'
          , 'category'      : 'object_print'
          , 'action'        : 'resource_print'
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
      },

      {    'id'             : 'Purchase Order'
         , 'meta_type'      : 'ERP5 Purchase Order'
         , 'title'          : 'Purchase Order'
         , 'description'    : """\
A Purchase..."""
         , 'icon'           : 'organisation_icon.gif'
         , 'product'        : 'ERP5'
         , 'factory'        : 'addOrder'
         , 'immediate_view' : 'purchase_order_view'
         , 'actions'        :
        ( { 'id'            : 'view'
          , 'name'          : 'View'
          , 'category'      : 'object_view'
          , 'action'        : 'purchase_order_view'
          , 'permissions'   : (
              Permissions.View, )
          }
        , { 'id'            : 'print'
          , 'name'          : 'Print'
          , 'category'      : 'object_print'
          , 'action'        : 'resource_print'
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
        , { 'id'            : 'history'
          , 'name'          : 'History'
          , 'category'      : 'object_view'
          , 'action'        : 'history_view'
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
      },

      {    'id'             : 'Purchase Order Module'
         , 'meta_type'      : 'ERP5 Folder'
         , 'title'          : 'Purchase Order Module'
         , 'description'    : """\
An Order..."""
         , 'icon'           : 'folder_icon.gif'
         , 'product'        : 'ERP5Type'
         , 'factory'        : 'addFolder'
         , 'immediate_view' : 'folder_view'
         , 'allowed_content_types': ('Purchase Order',
                                      )
         , 'actions'        :
        ( { 'id'            : 'view'
          , 'name'          : 'View'
          , 'category'      : 'object_view'
          , 'action'        : 'purchase_order_list'
          , 'permissions'   : (
              Permissions.View, )
          }
        , { 'id'            : 'print'
          , 'name'          : 'Print'
          , 'category'      : 'object_print'
          , 'action'        : 'resource_print'
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
      },


      {    'id'             : 'Account Module'
         , 'meta_type'      : 'ERP5 Folder'
         , 'title'          : 'Account Module'
         , 'description'    : """ Holds Account objects"""
         , 'icon'           : 'folder_icon.gif'
         , 'product'        : 'ERP5Type'
         , 'factory'        : 'addFolder'
         , 'immediate_view' : 'folder_view'
         , 'allowed_content_types': ('Account',
                                      )
         , 'actions'        :
        ( { 'id'            : 'view'
          , 'name'          : 'View'
          , 'category'      : 'object_view'
          , 'action'        : 'account_list'
          , 'permissions'   : (
              Permissions.View, )
          }
        , { 'id'            : 'print'
          , 'name'          : 'Print'
          , 'category'      : 'object'
          , 'action'        : 'folder_print'
          , 'permissions'   : (
              Permissions.View, )
          }
        , { 'id'            : 'search'
          , 'name'          : 'Search'
          , 'category'      : 'object'
          , 'action'        : 'folder_search'
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
      },

      {    'id'             : 'Account'
         , 'meta_type'      : 'ERP5 Account'
         , 'title'          : 'Account'
         , 'description'    : """ An Account is an abstract object which stores amounts of currencies."""
         , 'icon'           : 'organisation_icon.gif'
         , 'product'        : 'ERP5'
         , 'factory'        : 'addAccount'
         , 'immediate_view' : 'account_view'
         , 'allowed_content_types': ('Account',
                                     )
         , 'actions'        :
        ( { 'id'            : 'view'
          , 'name'          : 'View'
          , 'category'      : 'object_view'
          , 'action'        : 'account_view'
          , 'permissions'   : (
              Permissions.View, )
          }
        , { 'id'            : 'print'
          , 'name'          : 'Print'
          , 'category'      : 'object'
          , 'action'        : 'folder_print'
          , 'permissions'   : (
              Permissions.View, )
          }
        , { 'id'            : 'search'
          , 'name'          : 'Search'
          , 'category'      : 'object'
          , 'action'        : 'folder_search'
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
        , { 'id'            : 'history'
          , 'name'          : 'History'
          , 'category'      : 'object_view'
          , 'action'        : 'history_view'
          , 'permissions'   : (
              Permissions.View, )
          }
        , { 'id'            : 'metadata'
          , 'name'          : 'Metadata'
          , 'category'      : 'object_view'
          , 'action'        : 'metadata_edit'
          , 'permissions'   : (
              Permissions.TranslateContent, )
          }
        )
      },

      {    'id'             : 'Accounting Transaction Module'
         , 'meta_type'      : 'ERP5 Folder'
         , 'title'          : 'Accounting Transaction Module'
         , 'description'    : """ Holds Accounting Transaction objects"""
         , 'icon'           : 'folder_icon.gif'
         , 'product'        : 'ERP5Type'
         , 'factory'        : 'addFolder'
         , 'immediate_view' : 'folder_view'
         , 'allowed_content_types': ('Accounting Transaction',
                                     'Purchase Invoice Transaction',
                                     'Sale Invoice Transaction',
                                     )
         , 'actions'        :
        ( { 'id'            : 'view'
          , 'name'          : 'View'
          , 'category'      : 'object_view'
          , 'action'        : 'transaction_list'
          , 'permissions'   : (
              Permissions.View, )
          }
        , { 'id'            : 'print'
          , 'name'          : 'Print'
          , 'category'      : 'object'
          , 'action'        : 'folder_print'
          , 'permissions'   : (
              Permissions.View, )
          }
        , { 'id'            : 'search'
          , 'name'          : 'Search'
          , 'category'      : 'object'
          , 'action'        : 'folder_search'
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
      },


      {    'id'             : 'Accounting Transaction'
         , 'meta_type'      : 'ERP5 Accounting Transaction'
         , 'title'          : 'Accounting Transaction'
         , 'description'    : """ An order."""
         , 'icon'           : 'organisation_icon.gif'
         , 'product'        : 'ERP5'
         , 'factory'        : 'addAccountingTransaction'
         , 'immediate_view' : 'metadata_edit_form'
         , 'allowed_content_types': ('Accounting Transaction Line',
                                     )
         , 'actions'        :
        ( { 'id'            : 'view'
          , 'name'          : 'View'
          , 'category'      : 'object_view'
          , 'action'        : 'accounting_transaction_view'
          , 'permissions'   : (
              Permissions.View, )
          }
        , { 'id'            : 'print'
          , 'name'          : 'Print'
          , 'category'      : 'object'
          , 'action'        : 'folder_print'
          , 'permissions'   : (
              Permissions.View, )
          }
        , { 'id'            : 'search'
          , 'name'          : 'Search'
          , 'category'      : 'object'
          , 'action'        : 'folder_search'
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
        , { 'id'            : 'history'
          , 'name'          : 'History'
          , 'category'      : 'object_view'
          , 'action'        : 'history_view'
          , 'permissions'   : (
              Permissions.View, )
          }
        , { 'id'            : 'metadata'
          , 'name'          : 'Metadata'
          , 'category'      : 'object_view'
          , 'action'        : 'metadata_edit'
          , 'permissions'   : (
              Permissions.TranslateContent, )
          }
        )
      },


      {    'id'             : 'Accounting Transaction Line'
         , 'meta_type'      : 'ERP5 Accounting Transaction Line'
         , 'title'          : 'Accounting Transaction Line'
         , 'description'    : """ An order."""
         , 'icon'           : 'organisation_icon.gif'
         , 'product'        : 'ERP5'
         , 'factory'        : 'addAccountingTransactionLine'
         , 'immediate_view' : 'metadata_edit_form'
         , 'allowed_content_types': ('Accounting Transaction Line',
                                     )
         , 'actions'        :
        ( { 'id'            : 'view'
          , 'name'          : 'View'
          , 'category'      : 'object_view'
          , 'action'        : 'accounting_transaction_line_view'
          , 'permissions'   : (
              Permissions.View, )
          }
        , { 'id'            : 'print'
          , 'name'          : 'Print'
          , 'category'      : 'object'
          , 'action'        : 'folder_print'
          , 'permissions'   : (
              Permissions.View, )
          }
        , { 'id'            : 'search'
          , 'name'          : 'Search'
          , 'category'      : 'object'
          , 'action'        : 'folder_search'
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
        , { 'id'            : 'metadata'
          , 'name'          : 'Metadata'
          , 'category'      : 'object_view'
          , 'action'        : 'metadata_edit'
          , 'permissions'   : (
              Permissions.TranslateContent, )
          }
        )
      },




      {    'id'             : 'Purchase Invoice Transaction Line'
         , 'meta_type'      : 'ERP5 Invoice Transaction Line'
         , 'title'          : 'Purchase Invoice Transaction Line'
         , 'description'    : """ Holds Invoice objects"""
         , 'icon'           : 'organisation_icon.gif'
         , 'product'        : 'ERP5'
         , 'factory'        : 'addAccountingTransactionLine'
         , 'immediate_view' : 'metadata_edit_form'
         , 'allowed_content_types': ('Purchase Invoice Transaction Line',
                                     )
         , 'actions'        :
        ( { 'id'            : 'view'
          , 'name'          : 'View'
          , 'category'      : 'object_view'
          , 'action'        : 'purchase_invoice_transaction_line_view'
          , 'permissions'   : (
              Permissions.View, )
          }
        , { 'id'            : 'print'
          , 'name'          : 'Print'
          , 'category'      : 'object'
          , 'action'        : 'folder_print'
          , 'permissions'   : (
              Permissions.View, )
          }
        , { 'id'            : 'search'
          , 'name'          : 'Search'
          , 'category'      : 'object'
          , 'action'        : 'folder_search'
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
        , { 'id'            : 'metadata'
          , 'name'          : 'Metadata'
          , 'category'      : 'object_view'
          , 'action'        : 'metadata_edit'
          , 'permissions'   : (
              Permissions.TranslateContent, )
          }
        )
      },




      {    'id'             : 'Sale Invoice Transaction Line'
         , 'meta_type'      : 'ERP5 Invoice Transaction Line'
         , 'title'          : 'Sale Invoice Transaction Line'
         , 'description'    : """ Holds Invoice objects"""
         , 'icon'           : 'organisation_icon.gif'
         , 'product'        : 'ERP5'
         , 'factory'        : 'addAccountingTransactionLine'
         , 'immediate_view' : 'metadata_edit_form'
         , 'allowed_content_types': ('Sale Invoice Transaction Line',
                                     )
         , 'actions'        :
        ( { 'id'            : 'view'
          , 'name'          : 'View'
          , 'category'      : 'object_view'
          , 'action'        : 'sale_invoice_transaction_line_view'
          , 'permissions'   : (
              Permissions.View, )
          }
        , { 'id'            : 'print'
          , 'name'          : 'Print'
          , 'category'      : 'object'
          , 'action'        : 'folder_print'
          , 'permissions'   : (
              Permissions.View, )
          }
        , { 'id'            : 'search'
          , 'name'          : 'Search'
          , 'category'      : 'object'
          , 'action'        : 'folder_search'
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
        , { 'id'            : 'metadata'
          , 'name'          : 'Metadata'
          , 'category'      : 'object_view'
          , 'action'        : 'metadata_edit'
          , 'permissions'   : (
              Permissions.TranslateContent, )
          }
        )
      },

      {    'id'             : 'Currency Module'
         , 'meta_type'      : 'ERP5 Folder'
         , 'title'          : 'Currency Module'
         , 'description'    : """ Holds Currency objects"""
         , 'icon'           : 'folder_icon.gif'
         , 'product'        : 'ERP5Type'
         , 'factory'        : 'addFolder'
         , 'immediate_view' : 'folder_view'
         , 'allowed_content_types': ('Currency',)
         , 'actions'        :
        ( { 'id'            : 'view'
          , 'name'          : 'View'
          , 'category'      : 'object_view'
          , 'action'        : 'currency_list'
          , 'permissions'   : (
              Permissions.View, )
          }
        , { 'id'            : 'print'
          , 'name'          : 'Print'
          , 'category'      : 'object'
          , 'action'        : 'composant_list_print'
          , 'permissions'   : (
              Permissions.View, )
          }
        , { 'id'            : 'search'
          , 'name'          : 'Search'
          , 'category'      : 'object'
          , 'action'        : 'composant_search'
          , 'permissions'   : (
              Permissions.View, )
          }
        , { 'id'            : 'edit'
          , 'name'          : 'Edit'
          , 'category'      : 'object'
          , 'action'        : 'folder_edit_form'
          , 'permissions'   : (
              Permissions.ModifyPortalContent, )
          }
        , { 'id'            : 'sort_on'
          , 'name'          : 'Sort'
          , 'category'      : 'composant_list_sort_on'
          , 'action'        : 'object_sort'
          , 'permissions'   : (
              Permissions.View, )
          }
        , { 'id'            : 'list_ui'
          , 'name'          : 'Sort'
          , 'category'      : 'composant_list_ui'
          , 'action'        : 'object_ui'
          , 'permissions'   : (
              Permissions.View, )
          }

        )
      },

      {    'id'             : 'Currency'
         , 'meta_type'      : 'ERP5 Resource'
         , 'title'          : 'Currency'
         , 'description'    : """ Holds information about a currency """
         , 'icon'           : 'composant_icon.gif'
         , 'product'        : 'ERP5'
         , 'factory'        : 'addResource'
         , 'immediate_view' : 'currency_view'
         , 'allowed_content_types': ('Currency',)
         , 'actions'        :
        ( { 'id'            : 'view'
          , 'name'          : 'View'
          , 'category'      : 'object_view'
          , 'action'        : 'currency_view'
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
          , 'action'        : 'object_print'
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
        , { 'id'            : 'translation'
          , 'name'          : 'Transalation'
          , 'category'      : 'object_action'
          , 'action'        : 'translation_template_view'
          , 'permissions'   : (
              Permissions.ModifyPortalContent, )
          }
        , { 'id'            : 'history'
          , 'name'          : 'Historique'
          , 'category'      : 'object_view'
          , 'action'        : 'composant_history_view'
          , 'permissions'   : (
              Permissions.View )
          }
        )
      },

)

scriptable_type_information = (
      {    'id'             : 'Purchase Invoice Transaction'
         , 'meta_type'      : 'ERP5 Invoice'
         , 'title'          : 'Purchase Invoice Transaction'
         , 'description'    : """ Holds Invoice objects"""
         , 'icon'           : 'organisation_icon.gif'
         , 'product'        : 'ERP5'
         , 'immediate_view' : 'purchase_invoice_transaction_view'
         , 'permission'     : Permissions.AddPortalContent
         , 'constructor_path' : 'addPurchaseInvoice'
         , 'allowed_content_types': ('Purchase Invoice Transaction Line',
                                     )
         , 'actions'        :
        ( { 'id'            : 'view'
          , 'name'          : 'View'
          , 'category'      : 'object_view'
          , 'action'        : 'purchase_invoice_transaction_view'
          , 'permissions'   : (
              Permissions.View, )
          }
        , { 'id'            : 'print'
          , 'name'          : 'Print'
          , 'category'      : 'object'
          , 'action'        : 'folder_print'
          , 'permissions'   : (
              Permissions.View, )
          }
        , { 'id'            : 'search'
          , 'name'          : 'Search'
          , 'category'      : 'object'
          , 'action'        : 'folder_search'
          , 'permissions'   : (
              Permissions.View, )
          }
        , { 'id'            : 'history'
          , 'name'          : 'History'
          , 'category'      : 'object_view'
          , 'action'        : 'history_view'
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
        , { 'id'            : 'metadata'
          , 'name'          : 'Metadata'
          , 'category'      : 'object_view'
          , 'action'        : 'metadata_edit'
          , 'permissions'   : (
              Permissions.TranslateContent, )
          }
        )
      },

      {    'id'             : 'Sale Invoice Transaction'
         , 'meta_type'      : 'ERP5 Invoice'
         , 'title'          : 'Sale Invoice Transaction'
         , 'description'    : """ Holds Invoice objects"""
         , 'icon'           : 'organisation_icon.gif'
         , 'product'        : 'ERP5'
         , 'permission'     :  Permissions.AddPortalContent
         , 'constructor_path' : 'addSaleInvoice'
         , 'immediate_view' : 'sale_invoice_transaction_view'
         , 'allowed_content_types': ('Sale Invoice Transaction Line',
                                     )
         , 'actions'        :
        ( { 'id'            : 'view'
          , 'name'          : 'View'
          , 'category'      : 'object_view'
          , 'action'        : 'sale_invoice_transaction_view'
          , 'permissions'   : (
              Permissions.View, )
          }
        , { 'id'            : 'print'
          , 'name'          : 'Print'
          , 'category'      : 'object'
          , 'action'        : 'folder_print'
          , 'permissions'   : (
              Permissions.View, )
          }
        , { 'id'            : 'search'
          , 'name'          : 'Search'
          , 'category'      : 'object'
          , 'action'        : 'folder_search'
          , 'permissions'   : (
              Permissions.View, )
          }
        , { 'id'            : 'history'
          , 'name'          : 'History'
          , 'category'      : 'object_view'
          , 'action'        : 'history_view'
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
        , { 'id'            : 'metadata'
          , 'name'          : 'Metadata'
          , 'category'      : 'object_view'
          , 'action'        : 'metadata_edit'
          , 'permissions'   : (
              Permissions.TranslateContent, )
          }
        )
      },

)
