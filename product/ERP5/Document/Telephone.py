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
from Products.ERP5Type.Base import Base

from Products.ERP5.Document.Coordinate import Coordinate

import re

class Telephone(Coordinate, Base):
    """
        A telephone is a coordinate which stores a telephone number
        The telephone class may be used by multiple content types (ex. Fax,
        Mobile Phone, Fax, Remote Access, etc.).

        A telephone is a terminating leaf
        in the OFS. It can not contain anything.

        Telephone inherits from Base and
        from the mix-in Coordinate

        A list of I18N telephone codes can be found here::
          http://kropla.com/dialcode.htm
    """

    meta_type = 'ERP5 Telephone'
    portal_type = 'Telephone'
    add_permission = Permissions.AddPortalContent
    isPortalContent = 1
    isRADContent = 1

    # Declarative security
    security = ClassSecurityInfo()
    security.declareObjectProtected(Permissions.AccessContentsInformation) # ???????

    # The standard parser is used to read phone numbers
    # written in a standard syntax
    standard_parser = re.compile('\+(.*)\((.*)\)(.*)\-(.*)')

    # Declarative properties
    property_sheets = ( PropertySheet.Base
                      , PropertySheet.SimpleItem
                      , PropertySheet.Telephone
                      )


    security.declareProtected(Permissions.ModifyPortalContent, 'fromText')
    def fromText(self, coordinate_text,reindex_object=1):
        if coordinate_text is None:
            coordinate_text = ''
        if self.standard_parser.match(coordinate_text):
            (country, temp, area, number) = \
                self.standard_parser.match(coordinate_text).groups()
        else:
            country = area = ''
            number = coordinate_text
        self.edit(telephone_country = country,
                  telephone_area = area,
                  telephone_number = number,
                  reindex_object=reindex_object)

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
        text = '+'
        if self.telephone_country != None:
                text += self.telephone_country
        text += '(0)'
        if self.telephone_area != None:
          text += self.telephone_area
        text += '-'
        if self.telephone_number != None:
          text += self.telephone_number
        if text == '+(0)-' :
          return ''
        else:
          return text

    security.declareProtected(Permissions.View, 'getText')
    getText = asText

    security.declareProtected(Permissions.View, 'standardTextFormat')
    def standardTextFormat(self):
        """
          Returns the standard text formats for telephone numbers
        """
        return ("+33(0)6-62 05 76 14",)

