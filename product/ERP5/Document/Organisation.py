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

import zope.interface
from AccessControl import ClassSecurityInfo

from Products.ERP5Type import Permissions, PropertySheet, interfaces
from Products.ERP5.Document.Node import Node

class Organisation(Node):
    """
      An Organisation object holds the information about
      an organisation (ex. a division in a company, a company,
      a service in a public administration).

      Organisation objects can contain Coordinate objects
      (ex. Telephone, Url) as well a documents of various types.

      Organisation objects can be synchronized accross multiple
      sites.

      Organisation objects inherit from the MetaNode base class
      (one of the 5 base classes in the ERP5 universal business model)
    """

    meta_type = 'ERP5 Organisation'
    portal_type = 'Organisation'
    add_permission = Permissions.AddPortalContent

    zope.interface.implements(interfaces.INode)

    # Declarative security
    security = ClassSecurityInfo()
    security.declareObjectProtected(Permissions.AccessContentsInformation)

    # Declarative properties
    property_sheets = ( PropertySheet.Base
                      , PropertySheet.XMLObject
                      , PropertySheet.CategoryCore
                      , PropertySheet.DublinCore
                      , PropertySheet.Organisation
                      , PropertySheet.Mapping
                      , PropertySheet.Task
                      , PropertySheet.Reference
                      )


