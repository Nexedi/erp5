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

from AccessControl import ClassSecurityInfo

from Products.ERP5.Document.Resource import Resource
from Products.ERP5Type import Permissions, PropertySheet, Constraint, Interface
from Products.ERP5Type.Document.Folder import Folder


from zLOG import LOG

class ModeleMachine(Resource, Folder):
    """
      un modele de machine..
    """

    meta_type = 'CORAMY Modele Machine'
    portal_type = 'Modele Machine'
    add_permission = Permissions.AddPortalContent
    isPortalContent = 1
    isRADContent = 1

    # Declarative security
    security = ClassSecurityInfo()
    security.declareObjectProtected(Permissions.View)

    # Declarative properties
    property_sheets = ( PropertySheet.Base
                      , PropertySheet.CategoryCore
                      , PropertySheet.DublinCore
                      , PropertySheet.Resource
                      , PropertySheet.ModeleMachine
                      , PropertySheet.Reference

                      )

    # Hard Wired Variation List
    # XXX - may be incompatible with future versions of ERP5
    variation_base_category_list = ('option_machine',)

    # Factory Type Information
    factory_type_information = \
      {    'id'             : portal_type
         , 'meta_type'      : meta_type
         , 'description'    : """\
un modele..."""
         , 'icon'           : 'modele_machine_icon.gif'
         , 'product'        : 'Coramy'
         , 'factory'        : 'addModeleMachine'
         , 'immediate_view' : 'modele_machine_view'
         , 'allow_discussion'     : 1
         , 'allowed_content_types': ('Option Machine',
                                      )
         , 'filter_content_types' : 1
         , 'global_allow'   : 1
         , 'actions'        :
        ( { 'id'            : 'view'
          , 'name'          : 'View'
          , 'category'      : 'object_view'
          , 'action'        : 'modele_machine_view'
          , 'permissions'   : (
              Permissions.View, )
          },
        )
      }
