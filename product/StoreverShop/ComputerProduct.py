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

import Globals
from zLOG import LOG
from Products.CMFCore import CMFCorePermissions
from Products.CMFCore.CMFCorePermissions import View
from Products.CMFCore.CMFCorePermissions import ManageProperties
from AccessControl import ClassSecurityInfo
from Products.CMFCore.PortalContent import PortalContent
from Products.CMFDefault.DublinCore import DefaultDublinCoreImpl
from DateTime.DateTime import DateTime
from Products.ERP5Shop.Document.ShopProduct import ShopProduct
from ZODB.PersistentMapping import PersistentMapping
from Products.Base18.Document import Document18
from Products.ERP5Shop.Document.ShopOrder import ComputerVariantValue

factory_type_information = {
        'id': 'Computer Product',
        'meta_type': 'Storever Computer Product',
        'description': 'Use products to create an online shopping catalog',
        'product': 'StoreverShop',
        'icon': 'file_icon.gif',
        'factory': 'addComputerProduct',
        'filter_content_types': 0,
        'immediate_view': 'computerproduct_edit_form',
        'actions':
                ({'name': 'View',
                'id': 'view',
                'action': 'computerproduct_view',
                'permissions': ('View',),
                'category': 'object'},
               {'name': 'Edit',
                'id': 'edit',
                'action': 'computerproduct_edit_form',
                'permissions': ('Modify portal content',),
                'category': 'object'})
        }


def SecondSort(a,b):
    if a[1] > b[1]:
        return 1
    if a[1] < b[1]:
        return -1
    return 0


class ComputerProduct( ShopProduct, Document18 ):
    """
        ComputerProduct implements the first version
        of Storever online shop. It uses a very badly designed
        variation value system (a mix of tuple and dictionnary) and
        hard codes options. It should not be considered as a model.
    """
    meta_type='Storever Computer Product'
    portal_type='Computer Product'
    effective_date = expiration_date = None
    _isDiscussable = 1

    price = 0.0
    thumbnail = ''
    image = ''
    isCredit = 0
    credits = 0
    delivery_days = 0
    disk_price = {}
    memory_price = {}
    option_price = {}
    processor_price = {}
    default_variant = (80,1,128,1,(),'default partition','default task')
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


    def newVariationValue(self, context=None, variant=None, **kw):
        if context is not None:
          if hasattr(context, 'variant'):
            return ComputerVariantValue(context.variant)
          else:
            return None
        elif variant is not None:
          return ComputerVariantValue(variant)
        else:
          return None

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

    security.declareProtected(ManageProperties, 'setProcessorPrice')
    def setProcessorPrice(self, size, price):
        self.processor_price[size] = price

    security.declareProtected(ManageProperties, 'setDiskPrice')
    def setDiskPrice(self, size, price):
        self.disk_price[size] = price

    security.declareProtected(ManageProperties, 'setMemoryPrice')
    def setMemoryPrice(self, size, price):
        self.memory_price[size] = price

    security.declareProtected(ManageProperties, 'setOptionPrice')
    def setOptionPrice(self, option, price):
        self.option_price[option] = price
        
    security.declareProtected(View, 'getProcessorSizes')
    def getProcessorSizes(self):
        if not hasattr(self,'processor_price'):
            self.processor_price = PersistentMapping()
        return filter(lambda s: s.find('DISCONTINUED') <0, self.processor_price.keys())

    security.declareProtected(View, 'getDiskSizes')
    def getDiskSizes(self):
        if not hasattr(self,'disk_price'):
            self.disk_price = PersistentMapping()
        return filter(lambda s: s.find('DISCONTINUED') <0, self.disk_price.keys())
    
    security.declareProtected(View, 'getMemorySizes')
    def getMemorySizes(self):
        if not hasattr(self,'option_price'):
            self.memory_price = PersistentMapping()
        memory_price = self.memory_price
        return filter(lambda s: s.find('DISCONTINUED') <0, memory_price.keys())

    security.declareProtected(View, 'getOptions')
    def getOptions(self,pattern=''):
        if not hasattr(self,'option_price'):
            self.option_price = PersistentMapping()
        result = filter(lambda s,p=pattern: s.find(p) >= 0, self.option_price.keys())
        return filter(lambda s,p=pattern: s.find('DISCONTINUED') <0, result)	

    security.declareProtected(View, 'getProcessorValues')
    def getProcessorValues(self):
        """
            Return a sequence of tuples (option,price)
        """
        diskvalues = map(lambda i,product=self: (i, product.getProcessorPrice(i)),
                                                          self.getProcessorSizes())
        diskvalues.sort(SecondSort)
        return diskvalues

    security.declareProtected(View, 'getMemoryValues')
    def getMemoryValues(self):
        """
            Return a sequence of tuples (option,price)
        """
        diskvalues = map(lambda i,product=self: (i, product.getMemoryPrice(i)), self.getMemorySizes())
        diskvalues.sort(SecondSort)                     
        return diskvalues

    security.declareProtected(View, 'getDiskValues')
    def getDiskValues(self):
        """
            Return a sequence of tuples (option,price)
        """
        diskvalues = map(lambda i,product=self: (i, product.getDiskPrice(i)), self.getDiskSizes())
        diskvalues.sort(SecondSort)                     
        return diskvalues

    security.declareProtected(View, 'getOptionValues')
    def getOptionValues(self,pattern=''):
        """
            Return a sequence of tuples (option,price)
        """
        diskvalues = map(lambda i,product=self: (i, product.getOptionPrice(i)),
                                                            self.getOptions(pattern))
        diskvalues.sort(SecondSort)
        return diskvalues

    security.declareProtected(View, 'getProcessorPrice')
    def getProcessorPrice(self,size):
        return self.processor_price[size]

    security.declareProtected(View, 'getDiskPrice')
    def getDiskPrice(self,size):
        return self.disk_price[size]

    security.declareProtected(View, 'getMemoryPrice')
    def getMemoryPrice(self,size):
        return self.memory_price[size]

    security.declareProtected(View, 'getOptionPrice')
    def getOptionPrice(self,size):
        if self.option_price.has_key(size):
          return self.option_price[size]
        # Make sure this is not a discountinued option
        elif self.option_price.has_key('%s DISCONTINUED' % size):
          return self.option_price['%s DISCONTINUED' % size]
        else:
          return 0

    security.declareProtected(ManageProperties, 'deleteProcessorPrice')
    def deleteProcessorPrice(self,size):
        del self.processor_price[size]

    security.declareProtected(ManageProperties, 'deleteDiskPrice')
    def deleteDiskPrice(self,size):
        del self.disk_price[size]

    security.declareProtected(ManageProperties, 'deleteMemoryPrice')
    def deleteMemoryPrice(self,size):
        del self.memory_price[size]

    security.declareProtected(ManageProperties, 'deleteOptionPrice')
    def deleteOptionPrice(self,size):
        del self.option_price[size]


    def editThumbnail(self, thumbnail=None):
        if thumbnail is not None:
            self.thumbnail = thumbnail

    def editImage(self, image=None):
        if image is not None:
            self.image = image

    def _getPrice(self, context):
        """
          Compatibility
        """
        LOG("Context of Product", 0, str(context.__dict__))
        if hasattr(context,'variant'):
          return self.computePrice(context.variant)
        else:
          return self.price

    security.declareProtected(View, 'computePrice')
    def computePrice(self, variant):
        """
            variant is defined as:
                (color,processor,memory,disk,options,setup,config_url,
                root,boot,usr,home,var,tmp,swap,free)
        """
        processor_type = variant[1]
        memory_type = variant[2]
        disk_type = variant[3]
        base_price = self.price
        if self.processor_price.has_key(processor_type):
          base_price += self.processor_price[processor_type]
        # Make sure this is not a discountinued option
        elif self.processor_price.has_key('%s DISCONTINUED' % processor_type):
          base_price += self.processor_price['%s DISCONTINUED' % processor_type]
        else:
          processor_type = self.processor_price.keys()[0]
          base_price += self.processor_price[processor_type]
          variant[1] = processor_type
        if self.disk_price.has_key(disk_type):
          base_price += self.disk_price[disk_type]
        # Make sure this is not a discountinued option
        elif self.disk_price.has_key('%s DISCONTINUED' % disk_type):
          base_price += self.disk_price['%s DISCONTINUED' % disk_type]
        else:
          disk_type = self.disk_price.keys()[0]
          base_price += self.disk_price[disk_type]
          variant[3] = disk_type
        if self.memory_price.has_key(memory_type):
          base_price += self.memory_price[memory_type]
        # Make sure this is not a discountinued option
        elif self.memory_price.has_key('%s DISCONTINUED' % memory_type):
          base_price += self.memory_price['%s DISCONTINUED' % memory_type]
        else:
          memory_type = self.memory_price.keys()[0]
          base_price += self.memory_price[memory_type]
          variant[2] = memory_type
        setup = variant[5]
        if setup != '':
            base_price = base_price + self.getOptionPrice(setup)
        options_price = 0
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
        return "<p>Hardware:</p>" \
               "<ul><li>Color: %s</li><li>Processor: %s</li><li>Memory: %s</li><li>Disk: %s</li></ul>" \
               "<p>Options:</p>" \
               "<ul><li>Setup: %s</li>%s</ul>" \
               "<p>Configuration URL: %s</p>" \
               "<p>Partition:</p>" \
               "<ul><li>/root: %s</li><li>/boot: %s</li><li>/usr: %s</li><li>/home: %s</li><li>/var: %s</li><li>/tmp: %s</li><li>/swap: %s</li><li>/free: %s</li></ul>" \
               % (variant[0],variant[1],variant[2],variant[3],variant[5],option_text, \
                  variant[6],variant[7],variant[8],variant[9],variant[10],
                  variant[11],variant[12],variant[13],variant[14])

    security.declareProtected(View, 'shortVariant')
    def shortVariant(self, variant, REQUEST=None):
        return self.newVariationValue(variant=variant).asString()
        return "%s/%s/%s/%s/%s" % (variant[0],variant[1],variant[2],variant[3],variant[5])

    shortVariation = shortVariant
    security.declareProtected(View, 'shortVariation')

def addComputerProduct(self, id, title='', REQUEST=None):
        ob=ComputerProduct(id,title)
        self._setObject(id, ob)

Globals.InitializeClass(ComputerProduct)
