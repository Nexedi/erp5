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

import Globals, string
import zLOG
from Products.CMFCore import CMFCorePermissions
from Products.CMFCore.CMFCorePermissions import View
from Products.CMFCore.CMFCorePermissions import ManageProperties
from AccessControl import ClassSecurityInfo
from Products.CMFCore.PortalContent import PortalContent
from Products.CMFDefault.DublinCore import DefaultDublinCoreImpl
from DateTime.DateTime import DateTime
from Products.MMMShop.ShopProduct import ShopProduct
from ZODB.PersistentMapping import PersistentMapping
from Products.Base18.Document import Document18

factory_type_information = {
        'id': 'Simple Product',
        'meta_type': 'Storever Simple Product',
        'description': 'Use simple products to create products with variations',
        'product': 'StoreverShop',
        'icon': 'file_icon.gif',
        'factory': 'addSimpleProduct',
        'filter_content_types': 0,
        'immediate_view': 'simpleproduct_edit_form',
        'actions':
                ({'name': 'View',
                'id': 'view',
                'action': 'simpleproduct_view',
                'permissions': ('View',),
                'category': 'object'},
               {'name': 'Edit',
                'id': 'edit',
                'action': 'simpleproduct_edit_form',
                'permissions': ('Modify portal content',),
                'category': 'object'})
        }


def SecondSort(a,b):
    if a[1] > b[1]:
        return 1
    if a[1] < b[1]:
        return -1
    return 0


class SimpleProduct( ShopProduct, Document18 ):
    """
        A Product with variations
    """

    meta_type='Storever Simple Product'
    portal_type='Simple Product'
    effective_date = expiration_date = None
    _isDiscussable = 1

    price = 0.0
    thumbnail = ''
    image = ''
    isCredit = 0
    credits = 0
    delivery_days = 0
    default_variant = ()
    text = ''

    security = ClassSecurityInfo()

    def __init__( self
                , id
                , title=''
                , description=''
                ):
        DefaultDublinCoreImpl.__init__(self)
        self.id=id
        self.title=title
        self.description=description
        self.delivery_days=0
        self.processor_price = PersistentMapping()
        self.disk_price = PersistentMapping()
        self.memory_price = PersistentMapping()
        self.option_price = PersistentMapping()
        self.text = ''


    def SearchableText(self):
        """
            text for indexing
        """
        return "%s %s" % (self.title, self.description)

    security.declareProtected(ManageProperties, 'editProduct')
    def editProduct(self,
                    title=None,
                    description=None,
                    price=None,
                    isCredit=None,
                    credits=None,
                    category=None,
                    delivery_days=None,
		    product_path=None,
                    text=None):
        if title is not None:
            self.setTitle(title)
        if description is not None:
            self.setDescription(description)
        if price is not None:
            self.price = price
        if isCredit is not None:
            if isCredit == '1':
                self.isCredit = 1
            else:
                self.isCredit = 0

        if product_path is not None:
	    self.product_path = product_path
        if credits is not None:
            self.credits = int(credits)

        if category is not None:
            self.setSubject(category)

        if delivery_days is not None:
            self.delivery_days = int(delivery_days)

        if text is not None:
            self.text = text

        self.reindexObject()

    security.declareProtected(ManageProperties, 'setOptionPrice')
    def setOptionPrice(self, option, price):
        self.option_price[option] = price

    security.declareProtected(View, 'getOptions')
    def getOptions(self,pattern=''):
        if not hasattr(self,'option_price'):
            self.option_price = PersistentMapping()
        return filter(lambda s,p=pattern: s.find(p) >= 0, self.option_price.keys())

    security.declareProtected(View, 'getOptionValues')
    def getOptionValues(self,pattern=''):
        """
            Return a sequence of tuples (option,price)
        """
        diskvalues = map(lambda i,product=self: (i, product.getOptionPrice(i)), self.getOptions(pattern))
        diskvalues.sort(SecondSort)
        return diskvalues

    security.declareProtected(View, 'getOptionPrice')
    def getOptionPrice(self,size):
        if self.option_price.has_key(size):
          return self.option_price[size]
        else:
	  return 0

    security.declareProtected(ManageProperties, 'deleteOptionPrice')
    def deleteOptionPrice(self,size):
        del self.option_price[size]

    def editThumbnail(self, thumbnail=None):
        if thumbnail is not None:
            self.thumbnail = thumbnail

    def editImage(self, image=None):
        if image is not None:
            self.image = image

    security.declareProtected(View, 'computePrice')
    def computePrice(self, variant):
        """
            variant is defined as:
                (color,processor,memory,disk,options,setup,config_url,
                root,boot,usr,home,var,tmp,swap,free)
        """
        base_price = self.price
        options_price = 0.0
        for option in variant[4]:
            if option != '':
                options_price = options_price + self.getOptionPrice(option)
        return (base_price + options_price)

    security.declareProtected(View, 'renderVariant')
    def renderVariant(self, variant, REQUEST=None):
        option_text = ''
        for option in variant[4]:
            if option != '':
                option_text = option_text + "<li>%s</li>" % option
        return "<p>Options:</p><ul>%s</ul>" % option_text

    security.declareProtected(View, 'shortVariant')
    def shortVariant(self, variant, REQUEST=None):
        option_text = ''
        for option in variant[4]:
            if option != '':
                option_text = option_text + "%s/" % option
        return '<font size="-2"><i>%s</i></font>' % option_text

def addSimpleProduct(self, id, title='', REQUEST=None):
        ob=SimpleProduct(id,title)
        self._setObject(id, ob)

Globals.InitializeClass(SimpleProduct)
