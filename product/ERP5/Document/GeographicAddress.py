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

import string

class GeographicAddress(Coordinate, Base):
    """
        A geographic address holds a complete set of
        geographic coordinates including street, number,
        city, zip code, region.

        Geographic address is a terminating leaf
        in the OFS. It can not contain anything.

        Geographic address inherits from Base and
        from the mix-in Coordinate
    """
    meta_type = 'ERP5 Geographic Address'
    portal_type = 'Address'
    add_permission = Permissions.AddPortalContent
    isPortalContent = 1
    isRADContent = 1

    # Declarative security
    security = ClassSecurityInfo()
    security.declareObjectProtected(Permissions.View)

    # Declarative properties
    property_sheets = ( PropertySheet.Base
                      , PropertySheet.SimpleItem
                      , PropertySheet.GeographicAddress
                      )

    # Declarative interfaces
    __implements__ = ( Interface.Coordinate )

    # Factory Type Information
    factory_type_information = \
      {    'id'             : portal_type
         , 'meta_type'      : meta_type
         , 'description'    : """\
A geographic address holds a complete set of
geographic coordinates including street, number,
city, zip code, region."""
         , 'icon'           : 'geographic_address_icon.gif'
         , 'product'        : 'ERP5'
         , 'factory'        : 'addGeographicAddress'
         , 'immediate_view' : 'geographic_address_edit'
         , 'actions'        :
        ( { 'id'            : 'view'
          , 'name'          : 'View'
          , 'category'      : 'object_view'
          , 'action'        : 'geographic_address_edit'
          , 'permissions'   : (
              Permissions.View, )
          }
        , { 'id'            : 'print'
          , 'name'          : 'Print'
          , 'category'      : 'object_print'
          , 'action'        : 'geographic_address_print'
          , 'permissions'   : (
              Permissions.View, )
          }
        , { 'id'            : 'metadata'
          , 'name'          : 'Metadata'
          , 'category'      : 'object_edit'
          , 'action'        : 'metadata_edit'
          , 'permissions'   : (
              Permissions.View, )
          }
        , { 'id'            : 'translate'
          , 'name'          : 'Translate'
          , 'category'      : 'object_action'
          , 'action'        : 'translation_template_view'
          , 'permissions'   : (
              Permissions.TranslateContent, )
          }
        )
      }

    security.declareProtected(Permissions.View, 'asText')
    def asText(self, country=''):
        """
          Returns the address as a complete formatted string
          with street address, zip, city and region
        """
        if country=='France' or country=='france' or country=='fr' :
          return ('%s\n%s %s') % (self.street_address or '', 
                          self.zip_code or '', self.city or '')
        else :
          return ('%s\n%s %s') % (self.street_address or '', 
                        self.city or '', self.zip_code or '')

    security.declareProtected(Permissions.ModifyPortalContent, 'fromText')
    def fromText(self, coordinate_text):
        """
          Tries to recognize the coordinate_text to update
          this address
        """
        lines = string.split(coordinate_text, '\n')
        self.street_address = ''
        self.zip_code = ''
        self.city = ''
        zip_city = None
        if len(lines ) > 1:
          self.street_address = lines[0:-1]
          zip_city = string.split(lines[-1])
        elif len(lines ) > 0:
          self.street_address = ''
          zip_city = string.split(lines[-1])
        if zip_city:
          self.zip_code = zip_city[0]
          if len(zip_city) > 1:
            self.city = string.join(zip_city[1:])
        self.reindexObject()

    security.declareProtected(Permissions.View, 'standardTextFormat')
    def standardTextFormat(self):
        """
          Returns the standard text format for geographic addresses
        """
        return ("""\
c/o Jean-Paul Sartre
43, avenue Kleber
75118 Paris Cedex 5
""",
)

