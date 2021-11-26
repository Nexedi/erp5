# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2013 Nexedi SA and Contributors. All Rights Reserved.
#                    Aurélien Calonne <aurel@nexedi.com>
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

from AccessControl import ClassSecurityInfo
from Products.ERP5Type import Permissions, PropertySheet
from Products.ERP5Type.XMLObject import XMLObject
import suds
import base64
import lxml

class MailevaSOAPConnector(XMLObject):
  # CMF Type Definition
  meta_type = 'Maileva SOAP Connector'
  portal_type = 'Maileva SOAP Connector'

  # Declarative security
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  # Default Properties
  property_sheets = ( PropertySheet.Base
                    , PropertySheet.XMLObject
                    , PropertySheet.CategoryCore
                      )
  def submitRequest(self, recipient, sender, document):
    xml = self.generateRequestXML(recipient, sender, document)
    for xsd in [
      "https://webservices.recette.maileva.com/java/public/connector/ConnectorWebService?xsd=CommonSchema.xsd",
      "https://webservices.recette.maileva.com/java/public/connector/ConnectorWebService?xsd=MailevaSpecificSchema.xsd",
      "https://webservices.recette.maileva.com/java/public/connector/ConnectorWebService?xsd=MailevaPJSSchema.xsd"
    ]:
      schema_validator = lxml.etree.XMLSchema(file=xsd)
      if not schema_validator.validate(xml):
        raise ValueError('request xml %s is not validated')
    response =suds.client.Client(self.getUrlString()).service.submit(xml)
    return xml, response

  def _generateAddressLineList(self, entity):
    address_line_list = []
    address_line = entity.getDefaultAddressText()
    portal_type = entity.getPortalType()
    if portal_type == 'Person':
      address_line_list.append("%s %s" % (entity.getSocialTitleTitle(), entity.getTitle()))
    else:
      address_line_list.append("%s" % entity.getCorporateName())

    tmp_list = address_line.split('\n')
    if len(tmp_list) > 5:
      raise ValueError('Address %s has more than 5 lines' % tmp_list)
    for index in range(5):
      if index < len(tmp_list) - 1:
        address_line_list.append(tmp_list[index])
      else:
        address_line_list.append(None)
    if portal_type == "Person":
      address_line_list.append(tmp_list[-1])
    else:
      address_line_list.append("%s CEDEX" % tmp_list[-1])
    return address_line_list

  def generateRequestXML(self, recipient, sender, document, page_template='maileva_connection'):
    recipient_address_line_list= self._generateAddressLineList(recipient)
    sender_address_line_list = self._generateAddressLineList(sender)
    source_section_career_results = self.getPortalObject().portal_catalog(
      portal_type = 'Career',
      parent_uid = recipient.getUid(),
      subordination_uid = sender.getUid(),
      validation_state = 'open'
    )

    source_section_career = (source_section_career_results[0].getObject()if len(source_section_career_results) else recipient.getDefaultCareerValue() or '')
    if not source_section_career.getReference():
      raise ValueError('%s has no employee number defined' % source_section_career.getRelativeUrl())
    return getattr(document, page_template)(
      user = self.getUserId(),
      password = self.getPassword(),
      career_start_date = source_section_career.getStartDate(),
      employee_number = source_section_career.getReference(),
      recipient_region=recipient.getDefaultAddress().getRegionValue(),
      recipient = recipient,
      recipient_address_line_list = recipient_address_line_list,
      sender_region=sender.getDefaultAddress().getRegionValue(),
      sender_address_line_list = sender_address_line_list,
      content = base64.b64encode(document.getData())
    )
