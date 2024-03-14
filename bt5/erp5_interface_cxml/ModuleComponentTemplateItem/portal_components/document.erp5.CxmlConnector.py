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

import random, time, requests
from AccessControl import ClassSecurityInfo
from Products.ERP5Type import Permissions
from Products.ERP5Type.XMLObject import XMLObject
from zLOG import LOG

class CxmlConnector(XMLObject):
  # CMF Type Definition
  meta_type = 'ERP5 Cxml Connector'
  portal_type = 'CxmL Connector'

  # Declarative security
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  cxml_version = "1.2.061"

  security.declarePublic('getCxmlVersion')
  def getCxmlVersion(self):
    return self.cxml_version

  security.declarePublic('getPayloadId')
  def getPayloadId(self):
    host = self.REQUEST.HTTP_HOST
    date = str(int(time.time()))
    node = str(random.randint(0, 99))
    rand = str(random.randint(1000, 9999))
    return "%s.%s.%s@%s" %(date, node, rand, host)

  def getTextContentFromRequest(self):
    raise Exception(str(self.REQUEST.get('BODY')))

  def sendOutgoingRequest(self, text_content, portal_type="Cxml Document", causality='', follow_up='', temp_object=False):
    portal = self.getPortalObject()
    url = self.getUrlString()
    # Add password
    text_content = text_content.replace("REPLACE_WITH_PASSWORD", self.getPassword())
    response = requests.post(
      url,
      data=text_content,
      headers={'Content-Type': 'Content-Type: application/xml; charset="UTF-8"'},
      timeout=31)
    request_document = portal.cxml_document_module.newContent(
      portal_type=portal_type,
      temp_object=temp_object,
      text_content=text_content,
      causality=causality,
      follow_up=follow_up)
    response_document = portal.cxml_document_module.newContent(
      temp_object=temp_object,
      portal_type="Cxml Document",
      text_content=response.content,
      follow_up=follow_up,
      predecessor_value=request_document)
    request_document.setSuccessorValue(response_document)
    import transaction
    transaction.commit()
    et = response_document.getElementTree()
    try:
      assert int(et.xpath('/cXML/Response/Status')[0].get('code')) < 400
    except AssertionError:
      self.log(text_content)
      self.log(response.content)
      error_message = "Unexepected Response Status in response %s" %response_document.getRelativeUrl()
      raise AssertionError(error_message)
    return response_document

  def sendGetPendingRequest(self, message_type, last_received_timestamp):
    LOG("sendGetPendingRequest", 0, "Checking pending cXML messages")
    text_content = self.CxmlConnector_getGetPendingRequest(
      message_type=message_type,
      last_received_timestamp=last_received_timestamp
    )
    cxml_document_value = self.sendOutgoingRequest(text_content, temp_object=True)
    #cxml_document_value.validateXML(str(dtd))
    et = cxml_document_value.getElementTree()
    internal_id_element = et.xpath("/cXML/Response/GetPendingResponse/cXML/Message/DataAvailableMessage/InternalID")
    if len(internal_id_element):
      LOG("sendGetPendingRequest", 0, "Pending cXML message found")
      timestamp = et.get('timestamp')
      self.sendDataRequest(internal_id_element[0].text)
      self.sendGetPendingRequest(
        message_type=message_type,
        last_received_timestamp=timestamp)
    else:
      LOG("sendGetPendingRequest", 0, "No pending cXML message found")

  def sendDataRequest(self, internal_id):
    LOG("sendDataRequest", 0, "Downloading pending cXML message")
    portal = self.getPortalObject()
    text_content = self.CxmlConnector_getDataRequest(internal_id=internal_id)
    response = requests.post(
      url = "https://service-2.ariba.com/VendData.aw",
      data=text_content,
      headers={'Content-Type': 'Content-Type: application/xml; charset="UTF-8"'},
      timeout=31)
    request_document = portal.cxml_document_module.newContent(
      portal_type="Cxml Document",
      text_content=text_content)
    try:
      content_type = response.headers['Content-Type']
      size = response.headers['Content-Length']
    except KeyError as e:
      self.log(response.content)
      self.log(response.headers)
      raise e
    response_document = portal.cxml_multipart_document_module.newContent(
      portal_type="Cxml Multipart Document",
      data=response.content,
      size=size,
      content_type=content_type,
      causality_value=request_document)
    # Directly extract so that if there is an error
    # we can download document again
    LOG("sendDataRequest", 0, "Extracting downloaded cXML message %s" %response_document.getRelativeUrl())
    cxml_document_list = response_document.extract()
    for cxml_document in cxml_document_list:
      cxml_document.activate().process()
