##############################################################################
#
# Copyright (c) 2008 Nexedi SA and Contributors. All Rights Reserved.
#                    Yusei TAHARA <yusei@nexedi.com>
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
from Products.ERP5Type.Base import Base
from Products.ERP5Type.Utils import convertToUpperCase

from Products.ERP5.Document.Coordinate import Coordinate

import string

class InternetProtocolAddress(Base, Coordinate):
  """
  A internet protocol address holds a address of
  a computer on computer network using TCP/IP.
  """
  meta_type = 'ERP5 Internet Protocol Address'
  portal_type = 'Internet Protocol Address'
  add_permission = Permissions.AddPortalContent
  isPortalContent = 1
  isRADContent = 1

  # Declarative security
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  # Declarative properties
  property_sheets = ( PropertySheet.Base
                      , PropertySheet.SimpleItem
                      , PropertySheet.CategoryCore
                      , PropertySheet.InternetProtocolAddress
                      )

  # Declarative interfaces
  __implements__ = ( interfaces.ICoordinate, )

  def asText(self):
    """
    Return the address as a complete formatted string.
    """
    result = Coordinate.asText(self)
    if result is None:
      tmp = []
      for prop in PropertySheet.InternetProtocolAddress._properties:
        property_id = prop['id']
        getter_name = 'get%s' % convertToUpperCase(property_id)
        getter_method = getattr(self, getter_name)
        value = getter_method() or ''
        tmp.append('%s:%s' % (property_id, value))
      result = '\n'.join(tmp)
    return result

  def fromText(self, coordinate_text):
    """
    Try to import data from text.
    """
    property_id_list = [i['id'] for i in PropertySheet.InternetProtocolAddress._properties]

    for line in coordinate_text.split('\n'):
      if not ':' in line:
        continue
      name, value = line.split(':', 1)
      if name in property_id_list:
        setter_name = 'set%s' % convertToUpperCase(name)
        setter_method = getattr(self, setter_name)
        setter_method(value)

  def standardTextFormat(self):
    """
    Return the standard format string.
    """
    return """
host_name:mycomputer
ip_address:192.168.0.10
netmask:255.255.255.0
netmask_bit:24
network_address:192.168.0.0
broadcast_address:192.168.0.255
dns_server_ip_address:192.168.0.1
gateway_ip_address:192.168.0.1
network_interface:eth0"""
