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

from Products.ERP5SyncML.Conduit.VCardConduit import VCardConduit
from AccessControl import ClassSecurityInfo
from Products.ERP5Type import Permissions
from Products.ERP5SyncML.SyncCode import SyncCode
from zLOG import LOG, INFO, DEBUG, TRACE

class SharedVCardConduit(VCardConduit, SyncCode):
  """
  A conduit is in charge to read data from a particular structure,
  and then to save this data in another structure.
  
  SharedVCardConduit is a peace of code who provide GID.
  This GID are the same for all subscriber, so a same object could be updated
  by all the subscriber.
  """


  # Declarative security
  security = ClassSecurityInfo()
      
  def getGidFromObject(self, object):
    """
    return the Gid composed of FirstName_LastName generate with the object
    """
    gid_list = []
    if object.getFirstName() not in ('', None):
      gid_list.append(object.getFirstName())
    gid_list.append('_')
    if object.getLastName() not in ('', None):
      gid_list.append(object.getLastName())
    sql_kw = {}
    sql_kw['portal_type'] = 'Person'
    sql_kw['title'] = object.getTitle()
    sql_kw['id'] = '<'+object.getId()
    results = object.portal_catalog.countResults(**sql_kw)[0][0]
    LOG('getGidFromObject', DEBUG, 'getId:%s, getTitle:%s' % (object.getId(), object.getTitle()))
    LOG('getGidFromObject, number of results :', DEBUG, results)
    if int(results) > 0:
      gid_list.append('__')
      gid_list.append(str(int(results)+1))
    gid = ''.join(gid_list)
    LOG('getGidFromObject gid :', DEBUG, gid)
    return gid

  def getGidFromXML(self, vcard, namespace, gid_from_xml_list):
    """
    return the Gid composed of FirstName and LastName generate with a vcard
    """
    vcard_dict = self.vcard2Dict(vcard)
    gid_from_vcard_list = []
    if vcard_dict.has_key('first_name') and \
        vcard_dict['first_name'] not in ('', None):
      gid_from_vcard_list.append(vcard_dict['first_name'])
    gid_from_vcard_list.append('_')
    if vcard_dict.has_key('last_name') and \
        vcard_dict['last_name'] not in ('', None):
      gid_from_vcard_list.append(vcard_dict['last_name'])
    gid_from_vcard = ''.join(gid_from_vcard_list)
    LOG('getGidFromXML, gid_from_vcard :', DEBUG, gid_from_vcard)
    number = len([item for item in gid_from_xml_list if item.startswith(gid_from_vcard)])
    LOG('getGidFromXML, gid_from_xml_list :', DEBUG, gid_from_xml_list)
    LOG('getGidFromXML, number :', DEBUG, number)
    if number > 0:
      gid_from_vcard_list.append('__')
      gid_from_vcard_list.append(str(number+1)) 
      #it's mean for 3 persons a a a, the gid will be
      #a_, a___2 a___3
      gid_from_vcard = ''.join(gid_from_vcard_list)
    LOG('getGidFromXML, returned gid_from_vcard :', DEBUG, gid_from_vcard)
    return gid_from_vcard
  
