# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2004, 2005, 2006 Nexedi SARL and Contributors.
# All Rights Reserved.
##
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

import os
import unittest
from AccessControl.SecurityManagement import newSecurityManager
from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from Products.ERP5.Document.Document import ConversionError

class TestOoodResponse(ERP5TypeTestCase):

  manager_username = 'rie'
  manager_password = 'rie'
  quiet = 1
  run_all_test = 1

  def getTitle(self):
    return "TestOOoBatchMode"

  def login(self):
    uf = self.getPortal().acl_users
    uf._doAddUser(self.manager_username, self.manager_password, ['Manager'], [])
    user = uf.getUserById(self.manager_username).__of__(uf)
    newSecurityManager(None, user)

  def getBusinessTemplateList(self):
    return ('erp5_base',)

  def afterSetUp(self):
    self.login()
    # disable pref that configures the conversion server
    pref = self.getDefaultSystemPreference()
    if pref.getPreferenceState() != 'disabled':
      pref.disable()
    portal_skins = self.getSkinsTool()
    import_file_path = os.path.join(os.path.dirname(__file__),
                                    'test_document',
                                    'REF-en-001.odt')# Any text document will
                                                     # feet our needs
    import_file = open(import_file_path, 'rb')
    custom = portal_skins.custom
    addStyleSheet = custom.manage_addProduct['OFSP'].manage_addFile
    addStyleSheet(id='Base_getODTStyleSheet', file=import_file, title='',
      content_type='application/vnd.oasis.opendocument.text')
    addOOoTemplate = custom.manage_addProduct['ERP5OOo'].addOOoTemplate
    addOOoTemplate(id='ERP5Site_viewNothingAsOdt', title='')
    portal_skins.changeSkin(skinname=None)
    ERP5Site_viewNothingAsOdt = self.getPortal().ERP5Site_viewNothingAsOdt
    text = "<office:document-content xmlns:draw='urn:oasis:names:tc:opendocument:xmlns:drawing:1.0' xmlns:office='urn:oasis:names:tc:opendocument:xmlns:office:1.0' xmlns:text='urn:oasis:names:tc:opendocument:xmlns:text:1.0' xmlns:ooo='http://openoffice.org/2004/office' xmlns:number='urn:oasis:names:tc:opendocument:xmlns:datastyle:1.0' xmlns:dc='http://purl.org/dc/elements/1.1/' xmlns:meta='urn:oasis:names:tc:opendocument:xmlns:meta:1.0' xmlns:table='urn:oasis:names:tc:opendocument:xmlns:table:1.0' xmlns:dr3d='urn:oasis:names:tc:opendocument:xmlns:dr3d:1.0' xmlns:fo='urn:oasis:names:tc:opendocument:xmlns:xsl-fo-compatible:1.0' xmlns:style='urn:oasis:names:tc:opendocument:xmlns:style:1.0' xmlns:xforms='http://www.w3.org/2002/xforms' xmlns:form='urn:oasis:names:tc:opendocument:xmlns:form:1.0' xmlns:script='urn:oasis:names:tc:opendocument:xmlns:script:1.0' xmlns:ooow='http://openoffice.org/2004/writer' xmlns:svg='urn:oasis:names:tc:opendocument:xmlns:svg-compatible:1.0' xmlns:chart='urn:oasis:names:tc:opendocument:xmlns:chart:1.0' xmlns:dom='http://www.w3.org/2001/xml-events' xmlns:xlink='http://www.w3.org/1999/xlink' xmlns:xsd='http://www.w3.org/2001/XMLSchema' xmlns:xsi='http://www.w3.org/2001/XMLSchema-instance' xmlns:oooc='http://openoffice.org/2004/calc' xmlns:math='http://www.w3.org/1998/Math/MathML'  xmlns:tal='http://xml.zope.org/namespaces/tal'></office:document-content>"
    content_type = 'text/xml'
    ERP5Site_viewNothingAsOdt.pt_edit(text, content_type)

  def test_01_noExcNoFormatNoBatchMode(self):
    request = self.portal.REQUEST
    request.RESPONSE.setHeader('content-type', 'text/html')
    ERP5Site_viewNothingAsOdt = self.getPortal().ERP5Site_viewNothingAsOdt
    ERP5Site_viewNothingAsOdt(batch_mode=0)
    self.assertEqual('application/vnd.oasis.opendocument.text',
        request.RESPONSE.getHeader('content-type').split(';')[0])
    self.assertEqual('attachment; filename="ERP5Site_viewNothingAsOdt.odt"',
        request.RESPONSE.getHeader('content-disposition'))

  def test_01b_noExcEmptyFormatNoBatchMode(self):
    request = self.portal.REQUEST
    request.RESPONSE.setHeader('content-type', 'text/html')
    ERP5Site_viewNothingAsOdt = self.getPortal().ERP5Site_viewNothingAsOdt
    ERP5Site_viewNothingAsOdt(format='', batch_mode=0)
    self.assertEqual('application/vnd.oasis.opendocument.text',
        request.RESPONSE.getHeader('content-type').split(';')[0])
    self.assertEqual('attachment; filename="ERP5Site_viewNothingAsOdt.odt"',
        request.RESPONSE.getHeader('content-disposition'))

  def test_02_noExcNoFormatBatchMode(self):
    request = self.portal.REQUEST
    request.RESPONSE.setHeader('content-type', 'text/html')
    ERP5Site_viewNothingAsOdt = self.getPortal().ERP5Site_viewNothingAsOdt
    ERP5Site_viewNothingAsOdt(batch_mode=1)
    self.assertEqual('text/html',
        request.RESPONSE.getHeader('content-type').split(';')[0])

  def test_03_excPdfFormatNoBatchMode(self):
    request = self.portal.REQUEST
    request.RESPONSE.setHeader('content-type', 'text/html')
    ERP5Site_viewNothingAsOdt = self.getPortal().ERP5Site_viewNothingAsOdt
    # This assumes that a conversion error is raised because oood coordinates
    # are not defined in preferences.
    self.assertRaises(ConversionError, ERP5Site_viewNothingAsOdt,
                      batch_mode=0, format='pdf')
    self.assertEqual('text/html',
        request.RESPONSE.getHeader('content-type').split(';')[0])

  def test_04_excPdfFormatBatchMode(self):
    request = self.portal.REQUEST
    request.RESPONSE.setHeader('content-type', 'text/html')
    ERP5Site_viewNothingAsOdt = self.getPortal().ERP5Site_viewNothingAsOdt
    # This assumes that a conversion error is raised because oood coordinates
    # are not defined in preferences.
    self.assertRaises(ConversionError, ERP5Site_viewNothingAsOdt,
                         batch_mode=1, format='pdf')
    self.assertEqual('text/html', request.RESPONSE.getHeader('content-type').split(';')[0])

def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestOoodResponse))
  return suite

