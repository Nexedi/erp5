##############################################################################
#
# Copyright (c) 2002 Nexedi SARL and Contributors. All Rights Reserved.
#          Jean-Paul Smets-Solanes <jp@nexedi.com>
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

from Products.Coramy.Document.Item import Item
from Products.ERP5Type import Permissions, PropertySheet, Constraint, Interface
from AccessControl import ClassSecurityInfo

class Machine(Item):
    """
      une machine..
    """

    meta_type = 'CORAMY Machine'
    portal_type = 'Machine'
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
                      , PropertySheet.Amount
                      , PropertySheet.ModeleMachine
                      , PropertySheet.Reference
                      , PropertySheet.Machine
                      )

    # Factory Type Information
    factory_type_information = \
      {    'id'             : portal_type
         , 'meta_type'      : meta_type
         , 'description'    : """\
un modele..."""
         , 'icon'           : 'machine_icon.gif'
         , 'product'        : 'Coramy'
         , 'factory'        : 'addMachine'
         , 'immediate_view' : 'machine_view'
         , 'allow_discussion'     : 1
         , 'allowed_content_types': ('Machine',
                                      )
         , 'filter_content_types' : 1
         , 'global_allow'   : 1
         , 'actions'        :
        ( { 'id'            : 'view'
          , 'name'          : 'View'
          , 'category'      : 'object_view'
          , 'action'        : 'machine_view'
          , 'permissions'   : (
              Permissions.View, )
          },
        )
      }
