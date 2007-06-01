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
    security.declareObjectProtected(Permissions.AccessContentsInformation)

    # The standard parser is used to read phone numbers
    # written in a standard syntax
    # +[country]([area])[number]/[extension]
    # or in syntax retured by asText
    # +[country](0)[area]-[number]/[extension]
    standard_parser = re.compile('\+(?P<country>\d{,2})\(0\)(?P<area>\d+)-(?P<number>[^/]+)(\/(?P<ext>\d+))?')
    input_parser = re.compile('(\+(?P<country>\d*))?(\((?P<area>\d*)\))?(?P<number>[^/]*)(\/(?P<ext>\d+))?')

    # Declarative properties
    property_sheets = ( PropertySheet.Base
                      , PropertySheet.SimpleItem
                      , PropertySheet.Telephone
                      )


    security.declareProtected(Permissions.ModifyPortalContent, 'fromText')
    def fromText(self, coordinate_text):
        """ See ICoordinate.fromText """
        method = self._getTypeBasedMethod('fromText')
        if method is not None:
            return method(text=coordinate_text)
        
        if coordinate_text is None:
            coordinate_text = ''
        number_match = self.standard_parser.match(coordinate_text) or self.input_parser.match(coordinate_text)
        if not number_match:
          return
        number_dict = number_match.groupdict()
        self.log(number_dict)
        country = (number_dict.get('country', '') or '').strip()
        area = (number_dict.get('area', '') or '').strip()
        number = (number_dict.get('number', '') or '').strip().replace('-', ' ')
        extension = (number_dict.get('ext', '') or '').strip()
        self.edit(telephone_country = country,
                  telephone_area = area,
                  telephone_number = number, 
                  telephone_extension = extension)

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
        telephone_country = self.getTelephoneCountry()
        if telephone_country is not None:
          text += telephone_country

        text += '(0)'
        telephone_area = self.getTelephoneArea()
        if telephone_area is not None:
          text += telephone_area

        text += '-'
        telephone_number = self.getTelephoneNumber()
        if telephone_number is not None:
          text += telephone_number

        telephone_extension = self.getTelephoneExtension()
        if telephone_extension is not None:
          text += '/' + telephone_extension

        if text == '+(0)-':
          text = ''
        return text

    security.declareProtected(Permissions.View, 'getText')
    getText = asText

    security.declareProtected(Permissions.View, 'standardTextFormat')
    def standardTextFormat(self):
        """
          Returns the standard text formats for telephone numbers
        """
        return ("+33(0)6-62 05 76 14",)

