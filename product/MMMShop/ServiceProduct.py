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
import zLOG
from Products.CMFCore import CMFCorePermissions
from Products.CMFCore.CMFCorePermissions import View
from Products.CMFCore.CMFCorePermissions import ManageProperties
from AccessControl import ClassSecurityInfo
from Products.CMFCore.PortalContent import PortalContent
from Products.CMFDefault.DublinCore import DefaultDublinCoreImpl
from DateTime.DateTime import DateTime
from Products.StoreverShop.ComputerProduct import ComputerProduct
from ZODB.PersistentMapping import PersistentMapping
from Products.Base18.Document import Document18

factory_type_information = {
        'id': 'Service Product',
        'meta_type': 'Storever Service Product',
        'description': 'Use products to create an online shopping catalog',
        'product': 'StoreverShop',
        'icon': 'file_icon.gif',
        'factory': 'addServiceProduct',
        'filter_content_types': 0,
        'immediate_view': 'serviceproduct_edit_form',
        'actions':
                ({'name': 'View',
                'id': 'view',
                'action': 'serviceproduct_view',
                'permissions': ('View',),
                'category': 'object'},
               {'name': 'Edit',
                'id': 'edit',
                'action': 'serviceproduct_edit_form',
                'permissions': ('Modify portal content',),
                'category': 'object'})
        }


class ServiceProduct( ComputerProduct ):
    """
        A Link
    """
    meta_type='MMM Service Product'
    portal_type='Object'
    effective_date = expiration_date = None
    _isDiscussable = 1
    
    security = ClassSecurityInfo()    
    
def addServiceProduct(self, id, title='', REQUEST=None):
        ob=ComputerProduct(id,title)
        self._setObject(id, ob)

Globals.InitializeClass(ServiceProduct)
