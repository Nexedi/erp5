# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2007-2008 Nexedi SA and Contributors. All Rights Reserved.
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
from Products.ERP5Type.Globals import InitializeClass
from DocumentationHelper import DocumentationHelper
from Products.ERP5Type import Permissions
from Products.CMFCore.utils import getToolByName
from lxml import etree

class PortalTypePropertySheetDocumentationHelper(DocumentationHelper):
  """
    Provides documentation about a property sheet of a portal type
  """
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  security.declareProtected(Permissions.AccessContentsInformation, 'getType')
  def getType(self):
    """
    Returns the type of the documentation helper
    """
    return "Property Sheet"

  security.declareProtected(Permissions.AccessContentsInformation, 'getId')
  def getId(self):
    """
    Returns the id of the documentation helper
    """
    return self.uri.rsplit("/",1)[-1][:-3]

  security.declareProtected(Permissions.AccessContentsInformation, 'getTitle')
  def getTitle(self):
    """
    Returns the title of the documentation helper
    """
    return self.getDocumentedObject().name

  security.declareProtected(Permissions.AccessContentsInformation, 'getSourceCode')
  def getSourceCode(self):
    """
    Returns the source code the property sheet
    """
    from zLOG import LOG, INFO
    source_code = ""
    property_sheet_file = self.getDocumentedObject()
    if property_sheet_file is not None:
      property_sheet_file.seek(0)
      source_code = property_sheet_file.read()
      portal_transforms = getToolByName(self, 'portal_transforms')
      REQUEST = getattr(self, 'REQUEST', None)
      if REQUEST is not None:
        view_mode = REQUEST.get('portal_skin', 'View' )
      if portal_transforms is None:
        LOG('DCWorkflowScriptDocumentationHelper', INFO,
            'Transformation Tool is not installed. No convertion of python script to html')
        return source_code
      else:
        if view_mode == 'View':
          src_mimetype = 'text/x-python'
          mime_type = 'text/html'
          source_html = portal_transforms.convertTo(mime_type, source_code, mimetype=src_mimetype)
          return source_html
        else:
          src_mimetype = 'text/x-python'
          mime_type = 'text/xml'
          source_xml = portal_transforms.convertToData(mime_type, source_code,
                                                       mimetype=src_mimetype,
                                                       context=self, object=self,
                                                       filename=self.title_or_id()
                                                       )
          xpath = '//office:text//text:p'
          # parse content.xml
          xml_doc = etree.fromstring(source_xml)
          # the namespace text
          text_ns = xml_doc.nsmap['text']
          # all element text:p
          text_list = xml_doc.xpath(xpath, namespaces=xml_doc.nsmap)
          # all element wich have an text:style-name attribute
          parent_tag_list = xml_doc.xpath('//*[@text:style-name]', namespaces=xml_doc.nsmap)
          # Change the attribute text:style-name with a default value
          [parent_tag.attrib.update({'{%s}style-name' % text_ns: 'Preformatted_20_Text'}) \
                   for parent_tag in parent_tag_list]
          return ''.join([etree.tostring(text, pretty_print=True) for text in text_list])
    else:
      return source_code


InitializeClass(PortalTypePropertySheetDocumentationHelper)
