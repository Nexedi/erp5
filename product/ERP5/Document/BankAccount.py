##############################################################################
#
# Copyright (c) 2002-2005 Nexedi SARL and Contributors. All Rights Reserved.
#               Jean-Paul Smets-Solanes <jp@nexedi.com>
#               Kevin Deldycke <kevin@nexedi.com>
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

from Products.ERP5Type import Permissions, PropertySheet
from Products.ERP5.Document.Node import Node
from Products.ERP5.Document.Coordinate import Coordinate

class BankAccount(Node, Coordinate):
  """
      A bank account number holds a collection of numbers and codes
        (ex. SWIFT, RIB, etc.) which may be used to identify a bank account.

      A Bank Account is owned by a Person or an Organisation. A Bank Account
        contain Agents with Agent Privileges used by the owner to delegate the
        management of the bank account to trusted third-party Persons.
  """

  meta_type = 'ERP5 Bank Account'
  portal_type = 'Bank Account'
  add_permission = Permissions.AddPortalContent

  # Declarative security
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  # Declarative properties
  property_sheets = ( PropertySheet.CategoryCore
                    , PropertySheet.Task
                    , PropertySheet.Resource
                    , PropertySheet.Reference
                    , PropertySheet.BankAccount
                    )


  security.declareProtected(Permissions.AccessContentsInformation, 'getReference')
  def getReference(self, *args, **kw):
    """reference depends on the site configuration.
    """
    value = self._baseGetReference(*args, **kw)
    if value in (None, ''):
      # Try to get a skin from type name
      method = self._getTypeBasedMethod('getReference')
      if method is not None:
        return method(*args, **kw)
    return value

# XXX The following "helper methods" have been commented out, and kept in the
# code as an example.
# It might be a potential hazard to have the system automatically fill in the
# security keys. It is far more secure to have the user enter them manually,
# and then have the system doucle-check them.
# This can be accomplished in ERP5 through the use of Constraint.
#
#    security.declareProtected(Permissions.View, 'getBankCode')
#    def getBankCode(self, **kw):
#      """
#        Never return None.
#      """
#      if self.bank_code == None:
#        return ''
#      return self.bank_code
#
#
#    security.declareProtected(Permissions.View, 'getBranch')
#    def getBranch(self, **kw):
#      """
#        Never return None.
#      """
#      if self.branch == None:
#        return ''
#      return self.branch
#
#
#    security.declareProtected(Permissions.View, 'getBankAccountNumber')
#    def getBankAccountNumber(self, **kw):
#      """
#        Never return None.
#      """
#      if self.bank_account_number == None:
#        return ''
#      return self.bank_account_number
#
#
#    security.declareProtected(Permissions.View, 'getBankCountryCode')
#    def getBankCountryCode(self, **kw):
#      """
#        Never return None.
#      """
#      if self.bank_country_code == None:
#        return ''
#      return self.bank_country_code
#
#
#    security.declareProtected(Permissions.View, 'getIbanTextFormat')
#    def getIbanTextFormat(self):
#      """
#        Returns the standard IBAN text format
#      """
#      iban = self.getIban()
#      l = 4
#      s = "IBAN"
#      for i in range((len(iban) / l) + 1):
#        s += ' ' + iban[i*l : (i+1)*l]
#      return s.strip()
#
#
#    security.declareProtected(Permissions.View, 'getIbanTextFormat')
#    def getIban(self):
#      """
#        The International Bank Account Number of this bank account.
#        IBAN is an international standard for identifying bank accounts worldwide.
#      """
#      key          = self.getIbanKey()
#      country_code = self.getBankCountryCode()
#      bban         = self.getBban()
#      return (country_code + key + bban).upper().strip()
#
#
#    security.declareProtected(Permissions.View, 'getIbanKey')
#    def getIbanKey(self):
#      """
#        The IBAN key ensure the integry of the IBAN code.
#        It's calculated with the ISO 7064 method (known as "97-10 modulo").
#      """
#      # Construct the alpha to number translation table
#      table = {}
#      for i in range(26):
#        table[chr(65+i)] = str(10+i)
#      # Calcul the key
#      country_code = self.getBankCountryCode() + '00'
#      s = self.getBban() + country_code
#      n = ''
#      for c in s:
#        if c.isalpha():
#          n += table[c.upper()]
#        if c.isdigit():
#          n += c
#      key = str(98 - (int(n) % 97))
#      return key.zfill(2)
#
#
#    security.declareProtected(Permissions.View, 'getBban')
#    def getBban(self):
#      """
#        The Basic Bank Account Number (BBAN) is the last part of the IBAN.
#        Usualy it correspond to the national bank account number.
#      """
#      bank   = self.getBankCode()
#      branch = self.getBranch()
#      ban    = self.getBankAccountNumber()
#      key    = self.getBbanKey()
#      return (bank + branch + ban + key).upper().strip()
#
#
#    security.declareProtected(Permissions.View, 'getBbanTextFormat')
#    def getBbanTextFormat(self, sep=' '):
#      """
#        Returns a BBAN text format
#      """
#      bank   = self.getBankCode()
#      branch = self.getBranch()
#      ban    = self.getBankAccountNumber()
#      key    = self.getBbanKey()
#      return sep.join([bank, branch, ban, key]).upper().strip()
#
#
#    security.declareProtected(Permissions.View, 'getBbanKey')
#    def getBbanKey(self):
#      """
#        The BBAN key ensure the integry of the BBAN code.
#        This is the french BBAN key algorithm.
#      """
#      def transcode(string):
#        letter = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
#        digit  = '12345678912345678923456789'
#        for i in range(len(letter)):
#          string = string.replace(letter[i], digit[i])
#        return int(string)
#
#      bank   = self.getBankCode()
#      branch = self.getBranch()
#      ban    = self.getBankAccountNumber()
#      if len(bank + branch + ban) == 0:
#        return ''
#
#      bank   += ('0' * (5 - len(bank)))
#      branch += ('0' * (5 - len(branch)))
#
#      s = (bank + branch + ban).upper()
#      key = str(97 - ((transcode(s) * 100) % 97))
#      return key.zfill(2)
