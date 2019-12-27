
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

from Products.ERP5Type import Permissions, PropertySheet
from Products.ERP5Type.Utils import deprecated

from erp5.component.document.Coordinate import Coordinate
import re

class Telephone(Coordinate):
  """
    A telephone is a coordinate which stores a telephone number
    The telephone class may be used by multiple content types (ex. Fax,
    Mobile Phone, Fax, Remote Access, etc.).

    A telephone is a terminating leaf
    in the OFS. It can not contain anything.

    A list of I18N telephone codes can be found here::
      http://kropla.com/dialcode.htm
  """

  meta_type = 'ERP5 Telephone'
  portal_type = 'Telephone'
  add_permission = Permissions.AddPortalContent

  # Declarative security
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  # Declarative properties
  property_sheets = ( PropertySheet.CategoryCore
                    , PropertySheet.SortIndex
                    , PropertySheet.Telephone
                    )
  # This is a list of regex.
  # Each regex into the list handle a single (or should handle) input.
  # The list is a priority list,
  # be carefull to add a new regex.
  regex_list = [
    # Country, Area, City, Number, Extension*
    r"\+(?P<country>[\d ]+)(\(0\)|\ |\-)(?P<area>\d+)(\-|\ )(?P<city>\d+)(\-|\ )(?P<number>[\d\ \-]*)(?:\/)?(?P<ext>\d+|)",

    # Area, City, Number, Extension*
    r"^(\(0\)|0)?(?P<area>\d+)(\-|\ |\/)(?P<city>\d+)(\-|\ )(?P<number>[\d\ \-]*)(?:\/)?(?P<ext>\d+|)",
    r"^\+(\(0\)|0)+(?P<area>\d+)(\-|\ |\/)(?P<city>\d+)(\-|\ )(?P<number>[\d\ \-]*)(?:\/)?(?P<ext>\d+|)",
    # Country, Area, Number, Extension*
    # +11(0)1-11111111/111      or +11(0)1-11111111/      or +11(0)1-11111111
    # +11(0)1-1111-1111/111      or +11(0)1-1111-1111/      or +11(0)1-1111-1111
    # + 11 (0)1-11 11 01 01/111 or + 11 (0)1-11 11 01 01/ or + 11 (0)1-11 11 01 01
    # +11 (0)11 1011 1100/111   or +11 (0)11 1011 1100/   or +11 (0)11 1011 1100
    r"\+(?P<country>[\d\ ]*)\(0\)(?P<area>\d+)(\-|\ )(?P<number>[\d\ \-]*)(?:\/)?(?P<ext>\d+|)",


    # Country, Area, Number, Extension*
    # +11-1-11111111/111 or +11-1-11111111/ or +11-1-11111111
    r"\+(?P<country>\d+)-(?P<area>\d+)-(?P<number>[\d\ \-]*)(?:\/)?(?P<ext>\d+|)",

    # Missing area
    # +11(0)-11111111/111" or +11(0)-11111111/ or +11(0)-11111111
    r"\+(?P<country>\d+)\(0\)\-(?P<number>[\d\ ]*)(?:\/)?(?P<ext>\d+|)",

    # Country, Area, Number, Extension*
    # +11(1)11111111/111 or +11(1)11111111/ or +11(1)11111111
    r"\+(?P<country>\d+)\((?P<area>\d+)\)(?P<number>[\d\ ]*)(?:\/)?(?P<ext>\d+|)",

    # Country, Area, Number, Extension*
    # +111-1-11111111/111 or +111-1-11111111/ or +111-1-11111111
    r"\+(?P<country>\d+)-(?P<area>\d+)-(?P<number>[\d\ \-]*)(?:\/)?(?P<ext>\d+|)",

    # Missing country
    # +(0)1-11111111/111" or +(0)1-11111111/ or +(0)1-11111111
    r"\+\(0\)(?P<area>\d+)\-(?P<number>[\d\ ]*)(?:\/)?(?P<ext>\d+|)",

    # Missing Country and Area
    # +(0)-11111111/111" or +(0)-11111111/ or +(0)-11111111
    r"\+\(0\)\-(?P<number>[\d\ ]*)(?:\/)?(?P<ext>\d+|)",

    # Area, Number Extension*
    # Area between parenthesis.
    # (11)11111111/111 or (11)11111111/ or (11)11111111
    r"\((?P<area>\d+)\)(?P<number>[\d\ \-]*)(?:\/)?(?P<ext>\d+|)",

    # Missing country
    # +(1)11111111/111" or +(1)11111111/ or +(1)11111111
    r"\+\((?P<area>\d+)\)(?P<number>[\d\ \-]*)(?:\/)?(?P<ext>\d+|)",

    # Country, Area, Number and Extension*
    # Country space area space number slash extension or not
    # +11 1 011111111/1    or +11 1 011111111/  or +11 1 011111111
    # + 111 1 1101 101/111 or + 111 1 1101 101/ or + 111 1 1101 101/111
    r"\+(?P<space>[\ ]*)(?P<country>\d+)\ (?P<area>\d+)\ (?P<number>[\d\ ]*)(?:\/)?(?P<ext>\d+|)",

    # This regex is to handle two inputs very similar
    # but with different behavior
    # 111 11 11/111 or 111 11 11 or 111 11 11
    # will result in {'area':'', 'number':'111 11 11', 'ext':'111 or empty'}
    #
    # 111-11 11/111 or 111-11 11 or 111-11 11
    # will result in {'area':'111', 'number':'11 11', 'ext':'111 or empty'}
    r"^(?:0)?((?P<area>\d+)-)?(?P<number>[\d\-\ ]*)(?:\/)?(?P<ext>\d+|)$",

    # Area, Number, Extension*
    # It is a common input in France
    # and in Japan but with different behavior.
    # 011-111-1111/111 or 011-111-1111/ or 011-111-1111
    # will result in {'area':'11', 'number':'111-1111', \
    #                  'ext':'111 or empty'} <= France
    # will result in {'area':'011', 'number':'111-1111',
    #                  'ext':'111 or empty'} <= Japan
    # so we have here two regex:
    # To France: "^0(?P<area>\d+)-(?P<number>[\d\-\ ]*)(?:\/)?(?P<ext>\d+|)$",
    # To Japan: "^(?P<area>\d+)-(?P<number>[\d\-\ ]*)(?:\/)?(?P<ext>\d+|)$",
    r"^0(?P<area>\d+)-(?P<number>[\d\-\ ]*)(?:\/)?(?P<ext>\d+|)$",

    # Area, Number, Extension*
    # It is a common input in France and in Japan but with different behavior.
    # 011(111)1111/111 or 011(111)1111/ or 011(111)1111
    # will result in {'area':'11', 'number':'111)1111',
    #                  'ext':'111 or empty'} <= France
    # will result in {'area':'011', 'number':'111)1111',
    #                  'ext':'111 or empty'} <= Japan
    # so we have here two regex:
    #To France:
    # "^0(?P<area>\d+)\((?P<number>[\d\)\(\ \-]*)(?:\/)?(?P<ext>\d+|)$",
    #To Japan:
    # "^(?P<area>\d+)\((?P<number>[\d\)\(\ \-]*)(?:\/)?(?P<ext>\d+|)$",
    r"^0(?P<area>\d+)\((?P<number>[\d\)\(\ \-]*)(?:\/)?(?P<ext>\d+|)$",

    # Missing area
    # +11()11111111/111" or +11()11111111/ or +11()11111111
    r"\+(?P<country>\d+)\(\)(?P<number>[\d\ \-]*)(?:\/)?(?P<ext>\d+|)",

    # Country, area, number, extension*
    # Space between country and (0).
    # Space between (0) and area.
    # Space between area and number.
    # +111 (0) 1 111 11011/111 or +111 (0) 1 111 11011/ or +111 (0) 1 111 11011
    r"\+(?P<country>\d+)\ \(0\)\ (?P<area>\d+)\ (?P<number>[\d\ \-]*)(?:\/)?(?P<ext>\d+|)",

    # Country and number
    # (0) between country and number
    # +111 (0) 111111101-01/111 or +111 (0) 111111101-01/ or +111 (0) 111111101-01
    r"\+(?P<country>\d+)\ \(0\)\ (?P<number>[\d\ \-]*)(?:\/)?(?P<ext>\d+|)",

    # Country, area, number and extension*
    # +11 (11) 1111 1111/111 or +11 (11) 1111 1111/ or +11 (11) 1111 1111
    # +11 (11)-10111111/111  or +11 (11)-10111111/  or +11 (11)-10111111
    # +11(11)-10111111/111   or +11(11)-10111111/   or +11(11)-10111111
    # 1 (111) 1101-101/111   or 1 (111) 1101-101/   or 1 (111) 1101-101/
    r"(\+|)(?P<country>\d+)\ \((?P<area>\d+)\)(\ |\-|)(?P<number>[\d\ \-]*)(?:\/)?(?P<ext>\d+|)",

    # +110 1111111/111 or +110 1111111/ or +110 1111111
    r"\+(?P<country>\d+)\ (?P<number>[\d\ \-]*)(?:\/)?(?P<ext>\d+|)",

    # Missing country
    # 111/111-1111/111 or 111/111-1111/ or 111/111-1111
    r"(?P<area>\d+)\/(?P<number>[\d\ \-]*)(?:\/)?(?P<ext>\d+|)",

    # Country, area, number, extension*
    # Hyphen between country and area.
    # +11-1 11 11 01 11/111 or +11-1 11 11 01 11/ or +11-1 11 11 01 11
    r"\+(?P<country>\d+)\-(?P<area>\d+)\ (?P<number>[\d\ \-]*)(?:\/)?(?P<ext>\d+|)",

    # Missing area
    # +111-1101110/111 or +111-1101110/ or +111-1101110
    r"\+(?P<country>\d+)\-(?P<number>[\d\ \-]*)(?:\/)?(?P<ext>\d+|)",

    # Missing country
    # Dot between area number and telephone number.
    # 111.111.1111/111 or 111.111.1111/ or 111.111.1111
    r"(?P<area>\d+)\.(?P<number>[\d\ \-\.]*)(?:\/)?(?P<ext>\d+|)",

    # Country, area, number and extensioin*
    # (111 11) 111111/111     or (111 11) 111111/    or (111 11) 111111
    # (111 11) 111-11-11/111  or (111 11) 111-11-11/ or (111 11) 111-11-11
    # (111 11)101011/111      or (111 11)101011/     or (111 11)101011
    # +(111 11) 100-11-11/111 or +(111 11) 100-11-11 or +(111 11) 100-11-11
    r"(\+|)\((?P<country>\d+)\ (?P<area>\d+)\)(\ |)(?P<number>[\d\ \-]*)(?:\/)?(?P<ext>\d+|)",

    # Country and number
    # (+111)101111111/111  or (+111)101111111/  or (+111)101111111
    # (+111) 101111111/111 or (+111) 101111111/ or (+111) 101111111
    r"\(\+(?P<country>\d+)\)(\ |)(?P<number>[\d\ \-]*)(?:\/)?(?P<ext>\d+|)",

    # Country, area, number and extension*
    # (+11-111) 1111111/111 or (+11-111) 1111111/ or (+11-111) 1111111
    # (11-11) 111-1111/111  or (11-11) 111-1111/  or (11-11) 111-1111
    # (11-1) 1.111.111/111  or (11-1) 1.111.111/  or (11-1) 1.111.111
    r"\((\+|)(?P<country>\d+)\-(?P<area>\d+)\)(\ |\-|)(?P<number>[\d\ \-\.]*)(?:\/)?(?P<ext>\d+|)",

    # Country, area, number and extension*
    # + 111-11-1110111/111 or + 111-11-1110111/ or + 111-11-1110111
    # +111-11-1110111/111  or +111-11-1110111/  or +111-11-1110111
    # +111/1/1111 1100/111 or +111/1/1111 1100/ or +111/1/1111 1100
    r"\+(?P<spaces>[\ ]*)(?P<country>\d+)(\-|\/)(?P<area>\d+)(\-|\/)(?P<number>[\d\ \-\.]*)(?:\/)?(?P<ext>\d+|)",

    # + (111) 111-111/111 or + (111) 111-111/  or + (111) 111-111
    r"\+(?P<spaces>[\ ]*)\((?P<country>\d+)\)\ (?P<number>[\d\ \-\.]*)(?:\/)?(?P<ext>\d+|)"
  ]

  compiled_regex_list = [re.compile(pattern) for pattern in regex_list]

  compiled_input_regex_without_markup = re.compile('[0-9A-Za-z]')

  def _splitCoordinateText(self, coordinate_text):
    if coordinate_text is None:
      coordinate_text = ''

    # Removing the spaces of the begin and end.
    coordinate_text = str(coordinate_text).strip()

    # This regexp get the coordinate text
    # and extract number and letters
    input_without_markup = ''.join(self.compiled_input_regex_without_markup.\
                                                      findall(coordinate_text))
    # Test if coordinate_text has or not markups.
    if len(coordinate_text) > len(input_without_markup):
      number_match = None
      for regex in self._getRegexList():
        possible_number_match = regex.match(coordinate_text)
        if possible_number_match is not None:
          number_match = possible_number_match
          number_dict = number_match.groupdict()
          break
      if number_match is None:
        from zLOG import LOG, WARNING
        msg = "Doesn't exist a regex to handle this telephone: ", \
                                                               coordinate_text
        LOG('Telephone.fromText', WARNING, msg)
        number_dict = {'number': input_without_markup}
    else:
      number_dict = {'number': coordinate_text}

    country = number_dict.get('country') or ''
    area = number_dict.get('area') or ''
    city = number_dict.get('city') or ''
    number = number_dict.get('number') or ''
    extension = number_dict.get('ext') or ''
    if (country or area or city or number or extension):
      # Trying to get the country and area from dict,
      # but if it fails must be get from preference
      preference_tool = self.getPortalObject().portal_preferences
      if not country:
        country = preference_tool.getPreferredTelephoneDefaultCountryNumber('')
      if not area:
        area = preference_tool.getPreferredTelephoneDefaultAreaNumber('')
      if not city:
        city = preference_tool.getPreferredTelephoneDefaultCityNumber('')

      country =  country.strip()
      area = area.strip()
      city = city.strip()
      number = number.strip()
      extension = extension.strip()

      # Formating the number.
      # Removing any ")", "(", "-", "." and " "
      for token in ')(-. ':
        country = country.replace(token, '')
        number = number.replace(token, '')
    return country, area, city, number, extension

  security.declareProtected(Permissions.ModifyPortalContent, 'fromText')
  @deprecated
  def fromText(self, coordinate_text):
    """Save given data then continue parsing
    (deprecated because computed values are stored)
    """
    self._setCoordinateText(coordinate_text)
    method = self._getTypeBasedMethod('fromText')
    if method is not None:
      return method(text=coordinate_text)

    country, area, city, number, extension =\
                                     self._splitCoordinateText(coordinate_text)

    self.edit(telephone_country=country,
              telephone_area=area,
              telephone_city=city,
              telephone_number=number,
              telephone_extension=extension)

  security.declareProtected(Permissions.ModifyPortalContent, '_setText')
  _setText = fromText

  security.declareProtected(Permissions.AccessContentsInformation, 'asText')
  def asText(self):
    """
      Returns the telephone number in standard format
    """
    script = self._getTypeBasedMethod('asText')
    if script is not None:
      return script()

    if self.isDetailed():
      country = self.getTelephoneCountry('')
      area = self.getTelephoneArea('')
      city = self.getTelephoneCity('')
      number = self.getTelephoneNumber('')
      extension = self.getTelephoneExtension('')
    else:
      coordinate_text = self.getCoordinateText()
      country, area, city, number, extension =\
                                     self._splitCoordinateText(coordinate_text)

    if (country or area or city or number or extension):
      # Define the notation
      notation = self._getNotation()
      if notation:
        notation = notation.replace('<country>', country)
        notation = notation.replace('<area>', area)
        if city == "":
          notation = notation.replace('<city>-', '')
        else:
          notation = notation.replace('<city>', city)
        notation = notation.replace('<number>', number)
        notation = notation.replace('<ext>', extension)

      if extension == '':
        notation = notation.replace('/', '')

      return notation
    return ''

  security.declareProtected(Permissions.AccessContentsInformation,
                            'asURL')
  def asURL(self):
    """Returns a text representation of the Url if defined
    or None else.
    """
    if not self.isDetailed():
      coordinate_text = self.getCoordinateText()
      if coordinate_text:
        return 'tel:%s' % coordinate_text.replace(' ', '')

    telephone_country = self.getTelephoneCountry()
    if telephone_country is not None:
      url_string = '+%s' % telephone_country
    else :
      url_string = '0'

    telephone_area = self.getTelephoneArea()
    if telephone_area is not None:
      url_string += telephone_area

    telephone_city = self.getTelephoneCity()
    if telephone_city is not None:
      url_string += telephone_city

    telephone_number = self.getTelephoneNumber()
    if telephone_number is not None:
      url_string += telephone_number

    if url_string == '0':
      return None
    return 'tel:%s' % (url_string.replace(' ',''))

  security.declareProtected(Permissions.AccessContentsInformation, 'getText')
  getText = asText

  security.declareProtected(Permissions.AccessContentsInformation, 'standardTextFormat')
  def standardTextFormat(self):
    """
      Returns the standard text formats for telephone numbers
    """
    return ("+33(0)6-62 05 76 14",)

  security.declareProtected(Permissions.AccessContentsInformation, 'isDetailed')
  def isDetailed(self):
    return self.hasTelephoneCountry() or\
          self.hasTelephoneArea() or\
          self.hasTelephoneCity() or\
          self.hasTelephoneNumber() or\
          self.hasTelephoneExtension()

  def _getNotation(self):
    """
      Returns the notation that will be used by asText method.
    """
    # The notation can be changed.
    # But needs to have <country>, <area>, <city>, <number> and <ext>
    return "+<country>(0)<area>-<city>-<number>/<ext>"

  def _getRegexList(self):
    """
      Returns the regex list that will be used by fromText method.
    """
    return self.compiled_regex_list
