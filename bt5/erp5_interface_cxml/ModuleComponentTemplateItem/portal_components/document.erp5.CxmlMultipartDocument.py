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

import email.parser
from AccessControl import ClassSecurityInfo
from Products.ERP5Type.Accessor.Constant \
  import PropertyGetter as ConstantGetter
from Products.ERP5Type.XMLObject import XMLObject
from Products.ERP5Type.Permissions import AccessContentsInformation, ModifyPortalContent

class CxmlMultipartDocument(XMLObject):
  meta_type = 'ERP5 Cxml Multipart Document'
  portal_type = 'Cxml Multipart Document'
  isIndexable = ConstantGetter('isIndexable', value=False)

  security = ClassSecurityInfo()
  security.declareObjectProtected(AccessContentsInformation)

  def getTitle(self):
    return "%s %s" %(self.portal_type, self.getId())

  security.declareProtected(ModifyPortalContent, 'checkParts')
  def checkParts(self):
    "CHeck Parts"
    portal = self.getPortalObject()
    output = ""
    content = "content-length: %s\nContent-Type: %s\n%s" %(
      self.getSize(),
      self.getContentType(),
      self.getData()
    )
    message = email.Parser.Parser().parsestr(content)
    for part in message.walk():
      output += part.get_content_type() + "\n"
      if part.is_multipart():
        continue
      payload = part.get_payload(decode=0)
      cxml_document_list = []
      if part.get_content_type() == "application/pdf":
        filename = part.get_filename()
        pdf_document = portal.document_module.newContent(
          portal_type = "PDF",
          data = payload,
          filename = filename,
          title = filename.rstrip('.pdf'),
          version = "001",
          classification="collaborative/team",
          group="woelfel/wws",
          publication_section="verkauf/auftraege",
        )
        pdf_document.submit()
        cxml_document_list.append(pdf_document)
    self.setSuccessorValueList(self.getSuccessorValueList() + cxml_document_list)
    return output

  security.declareProtected(ModifyPortalContent, 'extract')
  def extract(self):
    "Extract Multipart Document and store the parts in corresponding modules"
    portal = self.getPortalObject()
    content = "content-length: %s\nContent-Type: %s\n%s" %(
      self.getSize(),
      self.getContentType(),
      self.getData()
    )
    message = email.Parser.Parser().parsestr(content)
    cxml_document_list = []
    pdf_document_list = []
    for part in message.walk():
      if part.is_multipart():
        continue
      payload = part.get_payload(decode=0)
      if part.get_content_type() == "application/pdf":
        filename = part.get_filename()
        pdf_document = portal.document_module.newContent(
          portal_type = "PDF",
          data = payload,
          filename = filename,
          title = filename.rstrip('.pdf'),
          version = "001",
          classification="collaborative/team",
          group="woelfel/wws",
          publication_section="verkauf/auftraege",
        )
        pdf_document.submit()
        pdf_document_list.append(pdf_document)
      else:
        if "<OrderRequest>" in payload:
          portal_type = "Cxml Order Request"
        else:
          portal_type = "Cxml Document"
        cxml_document_list.append(portal.cxml_document_module.newContent(
          portal_type=portal_type,
          text_content=payload,
          causality_value=self))
    for order_request in cxml_document_list:
      if order_request.getPortalType() == "Cxml Order Request":
        for pdf_document in pdf_document_list:
          pdf_document.setFollowUpValue(order_request)
    self.setSuccessorValueList(cxml_document_list + pdf_document_list)
    return cxml_document_list
