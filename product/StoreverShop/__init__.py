##############################################################################
#
# Copyright (c) 2002 Jean-Paul Smets
# Copyright (c) 2002 Nexedi SARL
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
# of the License, or (at your option) any later version, with the special
# provision that the authors explicitly grant hereby the right to link this
# program with any versions of the Qt library including non GPL versions
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
"""

ADD_FOLDERS_PERMISSION = 'Add portal folders'

import ComputerProduct
from Products.CMFCore import utils
from Products.CMFCore.DirectoryView import registerDirectory
import Products.MMMShop

# Aliases for previous mixed up version
__module_aliases__ = ( ( 'Products.MMMShop.ComputerProduct', ComputerProduct ),
                     )

#   ...and make sure we can find them in PTKBase when we do
#   'manage_migrate_content()'.
Products.MMMShop.ComputerProduct = ComputerProduct

contentClasses = ( ComputerProduct.ComputerProduct, )

contentConstructors = ( ComputerProduct.addComputerProduct, )

bases = contentClasses

boring_globals = globals()

import sys
this_module = sys.modules[ __name__ ]

z_bases = utils.initializeBasesPhase1( bases, this_module )

#Make the skins availiable as DirectoryViews
registerDirectory('skins/storever', globals())
registerDirectory('skins/zpt_storever', globals())
registerDirectory('skins/cm_storever', globals())

def initialize( context ):

    utils.initializeBasesPhase2( z_bases, context )

    utils.ContentInit( 'Storever Shop Content'
                     , content_types=contentClasses
                     , permission=ADD_FOLDERS_PERMISSION
                     , extra_constructors=contentConstructors
                     , fti = (
                          ComputerProduct.factory_type_information, )
                     ).initialize( context )
