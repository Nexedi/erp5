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
from Products.ERP5Type.Document.Folder import Folder

from Products.ERP5.Document.Coordinate import Coordinate

import string

class BankAccount(Folder, Coordinate):
    """
        A bank account number holds a collection of numbers
        and codes (ex. SWIFT, RIB, etc.) which may be used to
        identify a bank account.

        A bank account is a terminating leaf
        in the OFS. It can not contain anything.

        BankAccount inherits from Base and
        from the mix-in Coordinate
    """

    meta_type = 'ERP5 BankAccount'
    portal_type = 'BankAccount'
    add_permission = Permissions.AddPortalContent
    isPortalContent = 1
    isRADContent = 1

    # Declarative security
    security = ClassSecurityInfo()
    security.declareObjectProtected(Permissions.View)

    # Declarative properties
    property_sheets = ( PropertySheet.Base
                      , PropertySheet.SimpleItem
                      , PropertySheet.BankAccount
                      )

    # Declarative interfaces
    __implements__ = ( Interface.Coordinate )

    security.declareProtected(Permissions.View, 'asText')
    def asText(self):
        """
          Returns a string which identifies this bank account.
          Use IBAN if available, then an id code (ex. RIB; SWIFT)
          and finally a Bank / Branch / Number approach
        """
        if self.iban != '':
          return 'IBAN:%s' % self.iban
        if self.bank_account_id != '':
          return '%s:%s' % (self.bank_account_id_type, self.bank_account_id)
        if self.bank_name != '':
          return '%s / %s / %s' % (self.bank_name, self.bank_branch_name,
                                                    self.bank_account_number)
        return self.bank_account_number

    security.declareProtected(Permissions.ModifyPortalContent, 'fromText')
    def fromText(self, coordinate_text):
        """
          Tries to recognize the coordinate_text to update
          this bank account
        """
        self.iban = ''
        self.bank_name = ''
        self.bank_branch_name = ''
        self.bank_account_number = ''
        self.bank_account_id_type = ''
        self.bank_account_id = ''
        if coordinate_text[0:4] == 'IBAN:':
          self.iban = coordinate_text[5:]
          self.reindexObject()
          return
        coordinate_parts = string.split(coordinate_text, ':')
        if len(coordinate_parts) > 1:
          self.bank_account_id_type = coordinate_parts[0]
          self.bank_account_id = coordinate_parts[1]
          self.reindexObject()
          return
        coordinate_parts = string.split(coordinate_text, '/')
        if len(coordinate_parts) == 3:
          self.bank_name = coordinate_parts[0]
          self.bank_branch_name = coordinate_parts[1]
          self.bank_account_number = coordinate_parts[2]
          self.reindexObject()
          return
        self.bank_account_number = coordinate_text
        self.reindexObject()

    security.declareProtected(Permissions.View, 'standardTextFormat')
    def standardTextFormat(self):
        """
          Returns the standard text formats for bank accounts
        """
        return ("""\
IBAN: FR76 3002 7175 3900 0410 2760 135
""", """\
CIC / Calais / 3900 0410 2760
""", """\
RIB: FR76 3002 7175 3900 0410 2760 135
""",
)

