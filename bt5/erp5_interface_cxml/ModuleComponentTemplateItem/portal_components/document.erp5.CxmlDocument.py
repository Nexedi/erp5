##############################################################################
#
# Copyright (c) 2024 Nexedi SA and Contributors. All Rights Reserved.
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly advised to contract a Free Software
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

from lxml import etree
from AccessControl import ClassSecurityInfo
from DateTime import DateTime
from io import BytesIO
from Products.ERP5Type.XMLObject import XMLObject
from Products.ERP5Type.Permissions import AccessContentsInformation

class CxmlDocument(XMLObject):
  meta_type = 'ERP5 Cxml Document'
  portal_type = 'Cxml Document'

  security = ClassSecurityInfo()
  security.declareObjectProtected(AccessContentsInformation)

  def getTitle(self):
    return self.getDocumentType()

  security.declareProtected(AccessContentsInformation, "getXmlDocument")
  def getXmlDocument(self, pretty_print=False, REQUEST=None):
    """Get XML document"""
    xml = self.getTextContent()
    if pretty_print:
      try:
        et = etree.fromstring(xml, parser=etree.XMLParser(encoding='utf-8', remove_blank_text=1))
      except (SyntaxError, ValueError):
        return xml
      # remove shared seecret text
      for shared_secret in et.findall(".//SharedSecret"):
        shared_secret.text = ''
      xml = etree.tostring(et, encoding='utf-8', pretty_print=1)
    if REQUEST is not None:
      REQUEST.RESPONSE.setHeader('Content-Type', 'text/xml')
    return xml

  security.declareProtected(AccessContentsInformation, "validateXML")
  def validateXML(self):
    portal = self.getPortalObject()
    dtd = portal.portal_skins.erp5_interface_cxml["cxml.1.2.061.cXML.dtd"]
    xml = self.getTextContent()
    f = BytesIO(str(dtd))
    dtd = etree.DTD(f)
    et = etree.fromstring(xml, parser=etree.XMLParser(encoding='utf-8'))
    result = dtd.validate(et)
    if not result:
      raise Exception(dtd.error_log.filter_from_errors()[0])

  def getElementTree(self):
    xml = self.getTextContent()
    try:
      et = etree.fromstring(xml, parser=etree.XMLParser(encoding='utf-8', remove_blank_text=1))
    except (SyntaxError, ValueError):
      return None
    return et

  security.declareProtected(AccessContentsInformation, "getDocumentType")
  def getDocumentType(self):
    et = self.getElementTree()
    if et is None:
      return
    message = et.find('Response') or et.find('Request')
    if not message:
      return
    el_list = list(message)
    if message.tag == 'Response':
      pos = 1
    else:
      pos = 0
    if len(el_list) >= pos+1:
      return el_list[pos].tag
    else:
      return message.tag

  security.declareProtected(AccessContentsInformation, 'getCreationDate')
  def getCreationDate(self):
    """Alias to getStartDate"""
    return self.getStartDate() # workaround to index start_date in catalog

  security.declareProtected(AccessContentsInformation, 'getStartDate')
  def getStartDate(self):
    """Get timestam from cXML content"""
    et = self.getElementTree()
    return DateTime(et.get("timestamp")).toZone('UTC')

  security.declareProtected(AccessContentsInformation, 'getPayloadId')
  def getPayloadId(self):
    """Get payloadID from cXML content"""
    et = self.getElementTree()
    return et.get("payloadID")

  security.declareProtected(AccessContentsInformation, 'getFrom')
  def getFrom(self):
    """Get From value from cXML content"""
    et = self.getElementTree()
    identity = et.xpath('/cXML/Header/From/Credential/Identity')
    if len(identity):
      return identity[0].text

  security.declareProtected(AccessContentsInformation, 'getTo')
  def getTo(self):
    """Get To value from cXML content"""
    et = self.getElementTree()
    identity = et.xpath('/cXML/Header/To/Credential/Identity')
    if len(identity):
      return identity[0].text

  security.declareProtected(AccessContentsInformation, 'getStatusCode')
  def getStatusCode(self):
    """Get status code value from cXML content"""
    et = self.getElementTree()
    status = et.xpath('/cXML/Response/Status')
    if len(status):
      return status[0].get("code")

  def process(self):
    pass
