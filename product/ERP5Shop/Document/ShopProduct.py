##############################################################################
#
# Copyright (c) 2002 Nexedi SARL and Contributors. All Rights Reserved.
#                    Jean-Paul Smets-Solane <jp@nexedi.com>
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

from Products.CMFCore.utils import getToolByName
from Products.ERP5.Document.Resource import Resource
from Products.ERP5Type import Permissions, PropertySheet, Constraint, Interface
from Products.ERP5Type.XMLMatrix import XMLMatrix
from Products.MMMShop.ShopProduct import ShopProduct as MMMShopProduct

from zLOG import LOG

class ShopProduct(MMMShopProduct, Resource, XMLMatrix):
    """
      ERP5 Shop Product.

      An ERP5 Shop product
    """

    meta_type = 'ERP5 Shop Product'
    portal_type = 'Shop Product'
    add_permission = Permissions.AddERP5Content
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
                      , PropertySheet.DublinCore
                      , PropertySheet.Document
                      , PropertySheet.Price
                      , PropertySheet.Resource
                      , PropertySheet.ShopProduct
                      )

    # Hard Wired Variation List
    # XXX - may be incompatible with future versions of ERP5
    variation_base_category_list = ()

    # Factory Type Information
    factory_type_information = \
      {    'id'             : portal_type
         , 'meta_type'      : meta_type
         , 'description'    : """\
Un tissu est une resource variantable en couleur."""
         , 'icon'           : 'shop_product_icon.gif'
         , 'product'        : 'ERP5Shop'
         , 'factory'        : 'addShopProduct'
         , 'immediate_view' : 'shop_product_view'
         , 'allow_discussion'     : 1
         , 'allowed_content_types': ('File', 'Document', 'Image',
                                      )
         , 'filter_content_types' : 1
         , 'global_allow'   : 1
         , 'actions'        :
        ( { 'id'            : 'view'
          , 'name'          : 'View'
          , 'category'      : 'object_view'
          , 'action'        : 'shop_product_view'
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

    # Multiple Inheritance Resolving
    security.declareProtected(Permissions.ModifyPortalContent, 'edit')
    def edit(self, REQUEST=None, **kw):
      kw['force_update'] = 1
      Resource._edit(self, **kw)
      #LOG("Show kw",0,str(kw))
      MMMShopProduct.edit(self, REQUEST)

    _setProperty = Resource._setProperty
    setProperty = Resource.setProperty
    getProperty = Resource.getProperty   
    
    security.declareProtected(Permissions.ModifyPortalContent, '_setProductType')
    _setProductType = MMMShopProduct.setProductType

    def computePrice(self, REQUEST=None):
        return self.price

    def renderVariation(self, REQUEST=None):
        return ''

    def shortVariation(self, REQUEST=None):
        result = ''
        for c in REQUEST.categories:
          try:
            o = self.portal_categories.restrictedTraverse(c)
            result += '%s, ' % o.getTitle()
          except:
            pass
        if len(result) > 0:
          return result[0:-2]
        return result

    def _getPrice(self, context):
        """
          Private price depending in the context
        """
        return self._price

    def getPrice(self, context=None, REQUEST=None, **kw):
        """
          Public Generic Price Getter based on the context

          This Getter can be called

          - from the Web: parameters will be provided
            by the REQUEST object (context is None)

          - from a Python Script: parameters can
            are provided individually (kw is not None).
            Optional context object / REQUEST can be
            provided

          - from another Method: the context is passed
            (REQUEST is None and kw is None)

          Context instance is created

          This s


          The REQUEST can either hold a REQUEST object
          (resulting from an HTTP access) or a context
          object (ie. any object in the ZODB). The context
          can


        """
        return self._getPrice(self.asContext(context=context, REQUEST=REQUEST, **kw))

    def _getExchangedPrice(self, context):
        curmanager = getToolByName(self, 'portal_currency_manager')
        exchange_rate = curmanager.getMemberExchangeRate()
        price = float(self._getPrice(context)) / float(exchange_rate)
        return price

    def getExchangedPrice(self, context=None, REQUEST=None, **kw):
        context = self.asContext(context=context, REQUEST=REQUEST, **kw)
        return self._getExchangedPrice(context)

    security.declareProtected(Permissions.View, 'shortVariant')
    def shortVariant(self, variation_value, REQUEST=None):
        result = ''
        for c in variation_value.categories:
          result += '%s/' % c
        if len(result) > 0:  del result[-1]
        return result

    # Compatibility methods with early versions of StoreverShop
    security.declareProtected(Permissions.View, 'getProductPath')
    def getProductPath(self, REQUEST=None):
        return self.getRelativeUrl()

    security.declareProtected(Permissions.View, 'getOptionValues')
    def getOptionValues(self, REQUEST=None):
        return ()
