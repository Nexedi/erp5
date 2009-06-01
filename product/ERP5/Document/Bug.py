##############################################################################
#
# Copyright (c) 2005 Nexedi SARL and Contributors. All Rights Reserved.
#                    Yoshinori Okuji <yo@nexedi.com>
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
from Products.ERP5.Document.Ticket import Ticket

class Bug(Ticket):
    """Bug means a bug report, a feature request or an issue.
    """

    meta_type = 'ERP5 Bug'
    portal_type = 'Bug'
    add_permission = Permissions.AddPortalContent
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
                      , PropertySheet.DublinCore
                      , PropertySheet.Amount
                      , PropertySheet.Arrow
                      , PropertySheet.Price
                      , PropertySheet.Movement
                      , PropertySheet.Bug
                      )

    def SearchableText(self):
      """ Used by the catalog for basic full text indexing """
      full_text = []
      for message in self.contentValues(portal_type='Bug Line'):
        full_text.append(message.getTextContent(""))

      return """ %s %s %s """ % ( self.getTitle(),
                                  self.getDescription(),
                                  ' '.join(full_text))

    def manage_afterClone(self, item):
      Ticket.manage_afterClone(self, item)
      # delete existing bug lines
      self.manage_delObjects(list(self.contentIds(
                              filter=dict(portal_type='Bug Line'))))

