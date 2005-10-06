##############################################################################
#
# Copyright (c) 2005 Nexedi SARL and Contributors. All Rights Reserved.
#                    Alexandre Boeglin  <alex@nexedi.com>
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
from Products.ERP5Type.Base import Base

from Products.ERP5.Document.Coordinate import Coordinate

import re

class CreditCard(Coordinate, Base):
  """A credit card is a coordinate which stores a credit card information.

A credit card is a terminating leaf
in the OFS. It can not contain anything.

CreditCard inherits from Base and
from the mix-in Coordinate."""

  meta_type = 'ERP5 Credit Card'
  portal_type = 'Credit Card'
  add_permission = Permissions.AddPortalContent
  isPortalContent = 1
  isRADContent = 1

  # Declarative security
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.View) # ???????

  # The standard parser is used to read credit card numbers by taking
  # only the digits from the input string.
  standard_parser = re.compile('[0-9]+')

  # The output parser is used to generate a human readable credit card
  # number from a string
  output_parser = re.compile('.{1,4}')

  # Declarative properties
  property_sheets = ( PropertySheet.Base
                    , PropertySheet.SimpleItem
                    , PropertySheet.CreditCard
                    )


  security.declareProtected(Permissions.ModifyPortalContent, 'fromText')
  def fromText(self, coordinate_text,reindex_object=1):
      if coordinate_text is None:
        filtered_card_number = ''
      else:
        filtered_card_number =\
            ''.join(self.standard_parser.findall(coordinate_text))

      self.edit(card_number=filtered_card_number)

  security.declareProtected(Permissions.ModifyPortalContent, '_setText')
  _setText = fromText

  security.declareProtected(Permissions.View, 'asText')
  def asText(self):
      """
        Returns the telephone number in standard format
      """
      script = self._getTypeBasedMethod('asText')
      if script is not None:
        return script()

      if self.card_number is None:
        return ''

      text = ' '.join(self.output_parser.findall(self.card_number))
      return text

  security.declareProtected(Permissions.View, 'getText')
  getText = asText

  security.declareProtected(Permissions.View, 'standardTextFormat')
  def standardTextFormat(self):
      """
        Returns the standard text formats for telephone numbers
      """
      return ("1234 5678 9012 3456",)

