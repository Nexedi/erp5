# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2007 Nexedi SARL and Contributors. All Rights Reserved.
#          Fabien Morin <fabien.morin@gmail.com>
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
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
#
##############################################################################

from AccessControl import ClassSecurityInfo

from erp5.component.module.VCardConduit import VCardConduit

# pylint: disable=abstract-method
class SharedVCardConduit(VCardConduit):
  """
  A conduit is in charge to read data from a particular structure,
  and then to save this data in another structure.

  SharedVCardConduit is a piece of code who provide GID.
  This GID are the same for all subscriber, so a same object could be updated
  by all the subscriber.
  """

  # Declarative security
  security = ClassSecurityInfo()

  def getGidFromObject(self, object): # pylint: disable=redefined-builtin
    """
    return the Gid composed of FirstName_LastName generate with the object
    """
    gid_list = []
    if object.getFirstName():
      gid_list.append(object.getFirstName())
    gid_list.append('_')
    if object.getLastName():
      gid_list.append(object.getLastName())
    sql_kw = {'portal_type' : 'Person',
       'title' : object.getTitle(),
       'id' : {'query': object.getId(), 'range': 'max'}
       }
    results = object.portal_catalog.countResults(**sql_kw)[0][0]
    if int(results) > 0:
      gid_list.append('__')
      gid_list.append(str(int(results)+1))
    gid = ''.join(gid_list)
    return gid

  def getGidFromXML(self, vcard, gid_from_xml_list):
    """
    return the Gid composed of FirstName and LastName generate with a vcard
    """
    vcard_dict = self.vcard2Dict(vcard)
    gid_from_vcard_list = []
    if vcard_dict.get('first_name'):
      gid_from_vcard_list.append(vcard_dict['first_name'])
    gid_from_vcard_list.append('_')
    if vcard_dict.get('last_name'):
      gid_from_vcard_list.append(vcard_dict['last_name'])
    gid_from_vcard = ''.join(gid_from_vcard_list)
    number = len([item for item in gid_from_xml_list if item.startswith(gid_from_vcard)])
    if number:
      gid_from_vcard_list.append('__')
      gid_from_vcard_list.append(str(number+1))
      #it's mean for 3 persons a a a, the gid will be
      #a_, a___2 a___3
      gid_from_vcard = ''.join(gid_from_vcard_list)
    return gid_from_vcard
