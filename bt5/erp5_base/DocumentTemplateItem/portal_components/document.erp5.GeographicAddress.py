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

class GeographicAddress(Coordinate):
  """
      A geographic address holds a complete set of
      geographic coordinates including street, number,
      city, zip code, region.

      Geographic address is a terminating leaf
      in the OFS. It can not contain anything.
  """
  meta_type = 'ERP5 Geographic Address'
  portal_type = 'Address'
  add_permission = Permissions.AddPortalContent

  # Declarative security
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  # Declarative properties
  property_sheets = ( PropertySheet.SortIndex
                    , PropertySheet.CategoryCore
                    , PropertySheet.GeographicAddress
                    )


  def _splitCoordinateText(self, coordinate_text):
    """return street_address, zip_code, city tuple parsed from string
    """
    line_list = coordinate_text.splitlines()
    street_address = zip_code = city = ''
    zip_city = None
    if len(line_list) > 1:
      street_address = ''.join(line_list[0:-1])
      zip_city = line_list[-1].split()
    elif len(line_list):
      street_address = ''
      zip_city = line_list[-1].split()
    if zip_city:
      zip_code = zip_city[0]
      if len(zip_city) > 1:
        city = ''.join(zip_city[1:])
    return street_address, zip_code, city

  security.declareProtected(Permissions.AccessContentsInformation, 'asText')
  def asText(self):
    """
      Returns the address as a complete formatted string
      with street address, zip, and city
    """
    result = Coordinate.asText(self)
    if result is None:
      if self.isDetailed():
        street_address = self.getStreetAddress('')
        zip_code = self.getZipCode('')
        city = self.getCity('')
      else:
        street_address, zip_code, city = self._splitCoordinateText(self.getCoordinateText(''))
      result = '%s\n%s %s' % (street_address, zip_code, city)
    if not result.strip():
      return ''
    return result

  security.declareProtected(Permissions.ModifyPortalContent, 'fromText')
  @deprecated
  def fromText(self, coordinate_text):
    """Save given data then continue parsing
    (deprecated because computed values are stored)
    """
    self._setCoordinateText(coordinate_text)
    street_address, zip_code, city = self._splitCoordinateText(coordinate_text)
    self.setStreetAddress(street_address)
    self.setZipCode(zip_code)
    self.setCity(city)

  security.declareProtected(Permissions.AccessContentsInformation,
                            'standardTextFormat')
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

  security.declareProtected(Permissions.AccessContentsInformation, 'isDetailed')
  def isDetailed(self):
    return self.hasStreetAddress() or self.hasZipCode() or self.hasCity()
