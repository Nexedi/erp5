##############################################################################
#
# Copyright (c) 2002-2010 Nexedi SA and Contributors. All Rights Reserved.
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsibility of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# guarantees and support are strongly adviced to contract a Free Software
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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
##############################################################################

from lxml import etree
from cStringIO import StringIO
from zLOG import LOG
import transaction

class MagentoTestConnector:

  def __init__(self):
    """
    """
    from Products.ERP5.ERP5Site import getSite
    self.context = getSite()


  def generateResultHeader(self):
    # generate xml
    root = etree.Element("DataResultService")
    # Header part
    status_code = etree.SubElement(root, "StatusCode")
    status_code.text = "200"
    status_subcode = etree.SubElement(root, "StatusSubCode")
    status_subcode = "0"
    etree.SubElement(root, "ErrorDetails")
    return root

  def getPropertySheetDefinitionList(self, object):
    from Products.ERP5Type import interfaces, Constraint, Permissions, PropertySheet
    prop_list = []
    for property_sheet_name in object.getTypeInfo().getTypePropertySheetList():
      if "Magento" in property_sheet_name:
        base = getattr(PropertySheet, property_sheet_name, None)
        if base is not None:
          prop_list = [x['id'] for x in base._properties]
    return prop_list

  def UserGetList(self, *args, **kw):
    person_list = self.context.getPortalObject().magento_test_module.searchFolder(portal_type="Magento Test Person",
                                                                                 validation_state='validated')
    result_list = []
    
    for person in person_list:
      person = person.getObject()
      userInfo = {}
      
      userInfo["customer_id"] = person.getId().decode('utf-8')
      userInfo["firstname"] = person.getFirstname().decode('utf-8')
      userInfo["lastname"] = person.getLastname().decode('utf-8')
      userInfo["email"] = person.getEmail().decode('utf-8')
      
      result_list.append(userInfo)
      
    return "", result_list

  def UserGet(self, *args, **kw):
    if not kw.has_key('customer_id'):
      raise ValueError, "No customer_id in the arguments, got %s / %s" %(args, kw)

    customer_id = kw['customer_id']

    person_list = self.context.getPortalObject().magento_test_module.searchFolder(reference=customer_id,
                                                                                 portal_type="Magento Test Person",
                                                                                 validation_state='validated')

    if len(person_list) != 1:
      raise KeyError, "Error retrieving user with ID  %s" %(customer_id,)
    else:
      person = person_list[0].getObject()
    result_list = []
    user_info = {}
      
    user_info["customer_id"] = person.getId().decode('utf-8')
    user_info["firstname"] = person.getFirstname().decode('utf-8')
    user_info["lastname"] = person.getLastname().decode('utf-8')
    user_info["email"] = person.getEmail().decode('utf-8')
    
    result_list.append(user_info)
      
    return "", result_list

  def UserUpdate(self, *args, **kw):
    if not kw.has_key('customer_id'):
      raise ValueError, "No customer_id int the paramaters, got %s / %s" %(args, kw)

    customer_id = kw['customer_id']
    person_list = self.context.getPortalObject().magento_test_module.searchFolder(reference=user_id,
                                                                                 portal_type="Magento Test Person")
    if len(person_list) != 1:
      raise KeyError, "Error retrieving person with ID %s" %(customer_id)
    else:
      person = person_list[0].getObject()
    context = etree.iterparse(StringIO(kw['data']), events=('end',))
    person_dict = {}

    for k,v in kw.iteritems():
      person_dict[k] = v
    LOG("editing person %s with %s" %(person.getPath(), person_dict,), 300, "\n")
    person.edit(**person_dict)
    transaction.commit()

    # Return default xml
    return "", []


