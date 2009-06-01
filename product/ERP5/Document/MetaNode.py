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

from Products.ERP5Type import Permissions, PropertySheet, Constraint, interfaces
#from Products.ERP5.Core.MetaNode import MetaNode as CoreMetaNode
from Products.ERP5.Document.Organisation import Organisation as Node
#from Node import Node

#class MetaNode(Node, CoreMetaNode):
class MetaNode(Node):
    """
      A Node
    """

    meta_type = 'ERP5 MetaNode'
    portal_type = 'MetaNode'
    add_permission = Permissions.AddPortalContent
    isPortalContent = 1
    isRADContent = 1

    # Declarative security
    security = ClassSecurityInfo()
    security.declareObjectProtected(Permissions.AccessContentsInformation)

    # Declarative properties
    property_sheets = ( PropertySheet.Base
                      , PropertySheet.XMLObject
                      , PropertySheet.CategoryCore
                      , PropertySheet.DublinCore
                      )

    security.declareProtected( Permissions.ModifyPortalContent,
                               'immediateUpdateCapacity' )
    def immediateUpdateCapacity(self):
      """
        Lookup for capacities children of self and update capacity attributes
        by calling portal simulation (deferred)
      """
      portal_simulation =  getToolByName(self, 'portal_simulation')
      portal_simulation.updateCapacity(self)

    security.declareProtected( Permissions.ModifyPortalContent,
                               'updateCapacity' )
    def updateCapacity(self):
      """
        Lookup for capacities children of self and update capacity attributes
        by calling portal simulation (deferred)
      """
      self.activate().immediateUpdateCapacity()
