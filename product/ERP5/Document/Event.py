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

from Products.ERP5Type import Permissions, PropertySheet, Constraint, Interface
from Products.ERP5.Document.Movement import Movement
from Products.ERP5.Document.EmailDocument import EmailDocument
from Products.CMFCore.utils import getToolByName

class Event(EmailDocument, Movement):
    """
      Event is the base class for all events in ERP5.

      Event objects include emails, phone calls,

      The purpose of an Event object is to keep track
      of the interface between the ERP and third parties.

      Events have a start and stop date.

      Events may contain files and local role definitions.
    """

    meta_type = 'ERP5 Event'
    portal_type = 'Event'
    isPortalContent = 1
    isRADContent = 1
    isDelivery = 1
    
    # Declarative security
    security = ClassSecurityInfo()
    security.declareObjectProtected(Permissions.AccessContentsInformation)

    # Declarative properties
    property_sheets = ( PropertySheet.Base
                      , PropertySheet.XMLObject
                      , PropertySheet.CategoryCore
                      , PropertySheet.Document
                      , PropertySheet.DublinCore
                      , PropertySheet.Snapshot
                      , PropertySheet.Task
                      , PropertySheet.Url
                      , PropertySheet.TextDocument
                      , PropertySheet.Arrow
                      , PropertySheet.Movement
                      , PropertySheet.Event
                      , PropertySheet.Delivery
                      , PropertySheet.ItemAggregation
                     )

    security.declareProtected(Permissions.AccessContentsInformation,
                              'isAccountable')
    def isAccountable(self):
      """
        Returns 1 if this needs to be accounted
        Only account movements which are not associated to a delivery
        Whenever delivery is there, delivery has priority
      """
      return 1

    security.declareProtected(Permissions.AccessContentsInformation, 'defQuantity')
    def defQuantity(self):
      """
        Quantity is set automatically on Events.
      """
      return 1 # Provide opportunity to script this

