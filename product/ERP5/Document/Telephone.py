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

    # Declarative properties
    property_sheets = ( PropertySheet.Base
                      , PropertySheet.SimpleItem
                      , PropertySheet.Telephone
                      )
    
    # The notation always need to have:
    # <country> or <area> or <number> or <ext>
    # If uses a different tag it will be ignored.
    standard_dict = {
      # France
      '33' : {
        "regex_input_list" : [          
          # Country, Area, Number, Extension*
          # +33(0)2-27224896/999 or +33(0)2-27224896/ or +33(0)2-27224896
          "\+(?P<country>\d+)\(0\)(?P<area>\d+)\-(?P<number>[\d\ ]*)(?:\/)?(?P<ext>\d+|)", 
        
          # Missing country
          # +(0)2-27224896/999" or +(0)2-27224896/ or +(0)2-27224896
          "\+\(0\)(?P<area>\d+)\-(?P<number>[\d\ ]*)(?:\/)?(?P<ext>\d+|)",

          # Missing area
          # +33(0)-27224896/999" or +33(0)-27224896/ or +33(0)-27224896
          "\+(?P<country>\d+)\(0\)\-(?P<number>[\d\ ]*)(?:\/)?(?P<ext>\d+|)", 

          # Missing Country and Area 
          # +(0)-27224896/999" or +(0)-27224896/ or +(0)-27224896
          "\+\(0\)\-(?P<number>[\d\ ]*)(?:\/)?(?P<ext>\d+|)",
        
          # Country, Area, Number, Extension*
          # The area between parenthesis.
          # +33(629)024425/222 or +33(629)024425/ or +33(629)024425
          "^\+(?P<country>\d+)\((?P<area>\d+)\)(?P<number>[\d\ ]+)/?(?P<ext>\d+|)$", 
          # Area, Number Extension*
          # Area between parenthesis.
          # (22)27224897/333 or (22)27224897/ or (22)27224897
          "\((?P<area>\d+)\)(?P<number>[\d\ \-]*)(?:\/)?(?P<ext>\d+|)",
        
          # Area, Number, Extension*
          # Area followed by '-'
          # (22)-12345678/222 or (22)-12345678/ or (22)-12345678
          "\((?P<area>\d+)\)\-?(?P<number>[\d\ ]*)(?:\/)?(?P<ext>\d+|)",
        
          # Country, Area, Number and Extension*
          # Country space area space number slash extension or not
          # +33 2 098765432/1 or +33 2 098765432/ or +33 2 098765432
          "\+(?P<country>\d+)\ (?P<area>\d+)\ (?P<number>[\d\ ]*)(?:\/)?(?P<ext>\d+|)",
        
          # This regex is to handle two inputs very similar
          # but with different behavior
          # 631 22 43/999 or 631 22 43 or 631 22 43 
          # will result in {'area':'', 'country':'631 22 43', 'ext':'999 or empty'}
          #
          # 631-22 43/999 or 631-22 43 or 631-22 43 
          # will result in {'area':'631', 'country':'22 43', 'ext':'999 or empty'} 
          "^(?:0)?((?P<area>\d+)-)?(?P<number>[\d\-\ ]*)(?:\/)?(?P<ext>\d+|)$",
        
          # Area, Number, Extension*
          # 047-336-5411/999 or 047-336-5411/ or 047-336-5411
          "^0(?P<area>\d+)-(?P<number>[\d\-\ ]*)(?:\/)?(?P<ext>\d+|)$",
        
          # Area, Number, Extension*
          # 047(336)5411/999 or 047(336)5411/ or 047(336)5411
          "^0(?P<area>\d+)\((?P<number>[\d\)\(\ \-]*)(?:\/)?(?P<ext>\d+|)$"
        ],
        "notation" : "+<country>(0)<area>-<number>/<ext>"
      },
      # Brazil
      '55' : {
        "regex_input_list" : [
          # Country, Area, Number, Extension*
          # +55(2)27224896/999 or +55(2)27224896/ or +55(2)27224896
          "\+(?P<country>\d+)\((?P<area>\d+)\)(?P<number>[\d\ \-]*)(?:\/)?(?P<ext>\d+|)", 
          
          # Country, Area, Number, Extension*
          # +55-2-27224896/999 or +55-2-27224896/ or +55-2-27224896
          "\+(?P<country>\d+)-(?P<area>\d+)-(?P<number>[\d\ \-]*)(?:\/)?(?P<ext>\d+|)", 
        
          # Missing country
          # +(2)27224896/999 or +(2)27224896/ or +(2)27224896
          "\+\((?P<area>\d+)\)(?P<number>[\d\ \-]*)(?:\/)?(?P<ext>\d+|)",

          # Missing area
          # +55()-27224896/999 or +55()-27224896/ or +55()-27224896
          # +55()27224896/999 or +55()27224896/ or +55()27224896
          "\+(?P<country>\d+)\(\)(?:\-)?(?P<number>[\d\ ]*)(?:\/)?(?P<ext>\d+|)",
          
          # Missing Country and Area 
          # +()27224896/999 or +()27224896/ or +()27224896
          "\+\(\)(?P<number>[\d\ \-]*)(?:\/)?(?P<ext>\d+|)",
        
          # Country, Area, Number, Extension*
          # The area between parenthesis.
          # +55(629)024425/222 or +55(629)024425/ or +55(629)024425
          "^\+(?P<country>\d+)\((?P<area>\d+)\)(?P<number>[\d\ ]+)/?(?P<ext>\d+|)$", 

          # Area, Number Extension*
          # Area between parenthesis.
          # (22)27224897/333 or (22)27224897/ or (22)27224897
          "\((?P<area>\d+)\)(?P<number>[\d\ \-]*)(?:\/)?(?P<ext>\d+|)",
        
          # Country, Area, Number and Extension*
          # Country space area space number slash extension or not
          # +55 2 098765432/1 or +55 2 098765432/ or +55 2 098765432
          "\+(?P<country>\d+)\ (?P<area>\d+)\ (?P<number>[\d\ ]*)(?:\/)?(?P<ext>\d+|)",
        
          # This regex is to handle two inputs very similar
          # but with different behavior
          # 631 22 43/999 or 631 22 43 or 631 22 43 
          # will result in {'area':'', 'country':'631 22 43', 'ext':'999 or empty'}
          #
          # 631-22 43/999 or 631-22 43 or 631-22 43 
          # will result in {'area':'631', 'country':'22 43', 'ext':'999 or empty'} 
          "^((?P<area>\d+)-)?(?P<number>[\d\-\ ]*)(?:\/)?(?P<ext>\d+|)$",
        
          # Area, Number, Extension*
          # 047-336-5411/999 or 047-336-5411/ or 047-336-5411
          "^(?P<area>\d+)-(?P<number>[\d\-\ ]*)(?:\/)?(?P<ext>\d+|)$",
        
          # Area, Number, Extension*
          # 047(336)5411/999 or 047(336)5411/ or 047(336)5411
          "^(?P<area>\d+)\((?P<number>[\d\)\(\ \-]*)(?:\/)?(?P<ext>\d+|)$"
        ],
        "notation" : "+<country>(<area>)<number>/<ext>",
      },
       # Senegal
      '221' : {
        "regex_input_list" : [
          # Country, Area, Number, Extension*
          # +221(2)27224896/999 or +221(2)27224896/ or +221(2)27224896
          "\+(?P<country>\d+)\((?P<area>\d+)\)(?P<number>[\d\ \-]*)(?:\/)?(?P<ext>\d+|)", 
          
          # Country, Area, Number, Extension*
          # +221-2-27224896/999 or +221-2-27224896/ or +221-2-27224896
          "\+(?P<country>\d+)-(?P<area>\d+)-(?P<number>[\d\ \-]*)(?:\/)?(?P<ext>\d+|)", 
        
          # Missing country
          # +(2)27224896/999" or +(2)27224896/ or +(2)27224896
          "\+\((?P<area>\d+)\)(?P<number>[\d\ \-]*)(?:\/)?(?P<ext>\d+|)",

          # Missing area
          # +221()27224896/999" or +221()27224896/ or +221()27224896
          "\+(?P<country>\d+)\(\)(?P<number>[\d\ \-]*)(?:\/)?(?P<ext>\d+|)",
          
          # Missing Country and Area 
          # +()27224896/999" or +()27224896/ or +()27224896
          "\+\(\)(?P<number>[\d\ \-]*)(?:\/)?(?P<ext>\d+|)",
        
          # Country, Area, Number, Extension*
          # The area between parenthesis.
          # +221(629)024425/222 or +221(629)024425/ or +221(629)024425
          "^\+(?P<country>\d+)\((?P<area>\d+)\)(?P<number>[\d\ ]+)/?(?P<ext>\d+|)$", 
          # Area, Number Extension*
          # Area between parenthesis.
          # (22)27224897/333 or (22)27224897/ or (22)27224897
          "\((?P<area>\d+)\)(?P<number>[\d\ \-]*)(?:\/)?(?P<ext>\d+|)",
        
          # Country, Area, Number and Extension*
          # Country space area space number slash extension or not
          # +221 2 098765432/1 or +221 2 098765432/ or +221 2 098765432
          "\+(?P<country>\d+)\ (?P<area>\d+)\ (?P<number>[\d\ ]*)(?:\/)?(?P<ext>\d+|)",
        
          # This regex is to handle two inputs very similar
          # but with different behavior
          # 631 22 43/999 or 631 22 43 or 631 22 43 
          # will result in {'area':'', 'country':'631 22 43', 'ext':'999 or empty'}
          #
          # 631-22 43/999 or 631-22 43 or 631-22 43 
          # will result in {'area':'631', 'country':'22 43', 'ext':'999 or empty'} 
          "^((?P<area>\d+)-)?(?P<number>[\d\-\ ]*)(?:\/)?(?P<ext>\d+|)$",
        
          # Area, Number, Extension*
          # 047-336-5411/999 or 047-336-5411/ or 047-336-5411
          "^(?P<area>\d+)-(?P<number>[\d\-\ ]*)(?:\/)?(?P<ext>\d+|)$",
        
          # Area, Number, Extension*
          # 047(336)5411/999 or 047(336)5411/ or 047(336)5411
          "^(?P<area>\d+)\((?P<number>[\d\)\(\ \-]*)(?:\/)?(?P<ext>\d+|)$"
        ],
        "notation" : "+<country>(<area>)<number>/<ext>",
      },
      # Japan
      '81' : {
        "regex_input_list" : [
          # Country, Area, Number, Extension*
          # +81(2)27224896/999 or +81(2)27224896/ or +81(2)27224896
          "\+(?P<country>\d+)\((?P<area>\d+)\)(?P<number>[\d\ \-]*)(?:\/)?(?P<ext>\d+|)", 
          
          # Country, Area, Number, Extension*
          # +81-2-27224896/999 or +81-2-27224896/ or +81-2-27224896
          "\+(?P<country>\d+)-(?P<area>\d+)-(?P<number>[\d\ \-]*)(?:\/)?(?P<ext>\d+|)", 
        
          # Missing country
          # +(2)27224896/999" or +(2)27224896/ or +(2)27224896
          "\+\((?P<area>\d+)\)(?P<number>[\d\ \-]*)(?:\/)?(?P<ext>\d+|)",
          
          # Missing Country and Area 
          # +()27224896/999" or +()27224896/ or +()27224896
          "\+\(\)(?P<number>[\d\ \-]*)(?:\/)?(?P<ext>\d+|)",
        
          # Country, Area, Number, Extension*
          # The area between parenthesis.
          # +81(629)024425/222 or +81(629)024425/ or +81(629)024425
          "^\+(?P<country>\d+)\((?P<area>\d+)\)(?P<number>[\d\ ]+)/?(?P<ext>\d+|)$", 
          # Area, Number Extension*
          # Area between parenthesis.
          # (22)27224897/333 or (22)27224897/ or (22)27224897
          "\((?P<area>\d+)\)(?P<number>[\d\ \-]*)(?:\/)?(?P<ext>\d+|)",
        
          # Country, Area, Number and Extension*
          # Country space area space number slash extension or not
          # +81 2 098765432/1 or +81 2 098765432/ or +81 2 098765432
          "\+(?P<country>\d+)\ (?P<area>\d+)\ (?P<number>[\d\ ]*)(?:\/)?(?P<ext>\d+|)",
        
          # This regex is to handle two inputs very similar
          # but with different behavior
          # 631 22 43/999 or 631 22 43 or 631 22 43 
          # will result in {'area':'', 'country':'631 22 43', 'ext':'999 or empty'}
          #
          # 631-22 43/999 or 631-22 43 or 631-22 43 
          # will result in {'area':'631', 'country':'22 43', 'ext':'999 or empty'} 
          "^((?P<area>\d+)-)?(?P<number>[\d\-\ ]*)(?:\/)?(?P<ext>\d+|)$",
        
          # Area, Number, Extension*
          # 047-336-5411/999 or 047-336-5411/ or 047-336-5411
          "^(?P<area>\d+)-(?P<number>[\d\-\ ]*)(?:\/)?(?P<ext>\d+|)$",
        
          # Area, Number, Extension*
          # 047(336)5411/999 or 047(336)5411/ or 047(336)5411
          "^(?P<area>\d+)\((?P<number>[\d\)\(\ \-]*)(?:\/)?(?P<ext>\d+|)$"
        ],
        "notation" : "+<country>(<area>)<number>/<ext>",
      }
    }
    
    security.declareProtected(Permissions.ModifyPortalContent, 'fromText')
    def fromText(self, coordinate_text):
      """ See ICoordinate.fromText """
      method = self._getTypeBasedMethod('fromText')
      if method is not None:
        return method(text=coordinate_text)
      
      if coordinate_text is None:
        coordinate_text = ''

      # This regexp get the coordinate text 
      # and extract number and letters
      input_regex_without_markup = '[0-9A-Za-z]'
      input_without_markup = ''.join(re.findall(input_regex_without_markup,\
                                                coordinate_text))
      # Test if coordinate_text has or not markups.
      if len(coordinate_text) > len(input_without_markup):
        # Trying to get the regex list.
        input_parser_list = self._getRegexList(coordinate_text=coordinate_text)
        number_match = None
        for input_parser in input_parser_list:
          possible_number_match = re.match(input_parser, coordinate_text)
          if possible_number_match not in [None]:
            number_match = possible_number_match
            break
        if number_match == None:
          from zLOG import LOG, WARNING
          msg = "Doesn't exist a regex to handle this telephone: ", coordinate_text
          LOG('*** Telephone ***',WARNING,msg)
          return
        number_dict = number_match.groupdict()
      else:
        number_dict = {'number' : coordinate_text}

      country=number_dict.get('country','')
      area=number_dict.get('area','')
      number=number_dict.get('number','')
      ext=number_dict.get('ext','')

      if ((country in ['', None]) and \
          (area in ['', None]) and \
          (number in ['', None]) and \
          (ext in ['', None])):
        country = area = number = extension = ''
      else:
        # The country and area is trying to get from dict, 
        # but if it fails must be get from preference
        country_default_number = self.portal_preferences.getPreferredTelephoneDefaultCountryNumber()
        area_default_number = self.portal_preferences.getPreferredTelephoneDefaultAreaNumber()

        country = (number_dict.get('country') or \
                   country_default_number or \
                   '').strip()
        area = (number_dict.get('area') or \
                area_default_number or 
                '').strip()
        number = (number_dict.get('number') or '').strip()

        # Formating the number.
        # Removing any ")", "(", "-" and " "
        number = number.replace('-', '')
        number = number.replace(' ','')
        number = number.replace(')','')
        number = number.replace('(','')

        extension = (number_dict.get('ext') or '').strip()

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
      
      telephone_country = self.getTelephoneCountry() or ''
      telephone_area = self.getTelephoneArea() or ''
      telephone_number = self.getTelephoneNumber() or ''
      telephone_extension = self.getTelephoneExtension() or ''
     
      # If country, area, number, extension are blank 
      # the method should to return blank.
      if ((telephone_country == '') and \
          (telephone_area == '') and \
          (telephone_number == '') and \
          (telephone_extension == '')): 
        return ''
 
      # Trying to get the notation
      notation = self._getNotation(telephone_country=telephone_country)
      if notation not in [None, '']:
        notation=notation.replace('<country>',telephone_country)
        notation=notation.replace('<area>',telephone_area)
        notation=notation.replace('<number>',telephone_number)
        notation=notation.replace('<ext>',telephone_extension)

      return notation

    security.declareProtected(Permissions.AccessContentsInformation,
                              'asURL')
    def asURL(self):
      """Returns a text representation of the Url if defined
      or None else.
      """
      telephone_country = self.getTelephoneCountry()
      if telephone_country is not None:
        url_string = '+%s' % telephone_country
      else :
        url_string = '0'

      telephone_area = self.getTelephoneArea()
      if telephone_area is not None:
        url_string += telephone_area

      telephone_number = self.getTelephoneNumber()
      if telephone_number is not None:
        url_string += telephone_number

      if url_string == '0':
        return None
      return 'tel:%s' % (url_string.replace(' ',''))

    security.declareProtected(Permissions.View, 'getText')
    getText = asText

    security.declareProtected(Permissions.View, 'standardTextFormat')
    def standardTextFormat(self):
      """
        Returns the standard text formats for telephone numbers
      """
      return ("+33(0)6-62 05 76 14",)

    def _getRegexDict(self, index=None):
      """
        Returns a dict with Regex and Notations based from 
        country or region
      """
      # Trying to get the Regex Dict
      if index not in self.standard_dict.keys():
        index = self.portal_preferences.getPreferredTelephoneDefaultCountryNumber() or '33'
           
      return self.standard_dict.get(index)
    
    def _getRegexList(self, coordinate_text):
      """
        Returns the regex list.
      """
      # Trying to get a possible contry number
      country_regex = '((\+|)(?P<country>\d*))'
      country = re.match(country_regex, \
                       coordinate_text).groupdict().get('country','')
      regex_dict = self._getRegexDict(index=country)
      input_parser = regex_dict.get('regex_input_list')
      return input_parser
  
    def _getNotation(self, telephone_country):
      """
        Returns the notation that will be used by asText method.
      """
      regex_dict = self._getRegexDict(index=telephone_country)
      notation = regex_dict.get('notation')
      return notation
