# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2004, 2010 Nexedi SA and Contributors.
# All Rights Reserved.
#          Nicolas Delaby <nicolas@nexedi.com>
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
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
#
##############################################################################

import unittest
import os
from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from Products.ERP5Type.tests.utils import FileUpload
from unittest import expectedFailure

import six.moves.http_client
from six.moves import cStringIO as StringIO
from DateTime import DateTime

from lxml import etree

def makeFilePath(name):
  import Products.ERP5.tests
  return os.path.join(os.path.dirname(Products.ERP5.tests.__file__),
                      'test_data', name)

def makeFileUpload(name, as_name=None):
  if as_name is None:
    as_name = name
  path = makeFilePath(name)
  return FileUpload(path, as_name)

class TestWebDavSupport(ERP5TypeTestCase):
  """Test for WEBDAV access.
  """

  authentication = 'ERP5TypeTestCase:'

  def getTitle(self):
    return "Test WebDav Support"

  def getBusinessTemplateList(self):
    """
    Return the list of required business templates.
    """
    return ('erp5_base',
            'erp5_ingestion',
            'erp5_ingestion_mysql_innodb_catalog',
            'erp5_web',
            'erp5_dms',
            )

  def afterSetUp(self):
    pass

  def clearModule(self, module):
    module.manage_delObjects(list(module.objectIds()))
    self.tic()

  def beforeTearDown(self):
    self.clearModule(self.portal.document_module)
    self.clearModule(self.portal.web_page_module)

  def getDocumentModule(self):
    return self.portal.getDefaultModule('Text')

  def getWebPageModule(self):
    return self.portal.getDefaultModule('Web Page')

  def test_PUT_embedded_file(self):
    """Test a file can be uploaded on a document allowing embedded files
    """
    person = self.portal.person_module.newContent()
    self.tic()
    file_object = makeFileUpload('images/erp5_logo.png')
    response = self.publish(person.getPath() + '/erp5_logo.png',
                            request_method='PUT',
                            stdin=file_object,
                            basic=self.authentication)
    self.assertEqual(response.getStatus(), six.moves.http_client.CREATED)
    image = person['erp5_logo.png']
    self.assertEqual(image.getPortalType(), 'Embedded File')
    self.assertEqual(image.getContentType(), 'image/png')
    file_object.seek(0)
    self.assertEqual(image.getData(), file_object.read())

  def test_PUT_on_contributionTool(self):
    """Test Portal Contribution through Webdav calls
    Create a document
    """
    # Create a new document via FTP/DAV
    path = self.portal.portal_contributions.getPath()
    filename = 'P-DMS-Presentation.3.Pages-001-en.odp'
    file_object = makeFileUpload(filename)
    response = self.publish('%s/%s' % (path, filename),
                            request_method='PUT',
                            stdin=file_object,
                            basic=self.authentication)

    self.assertEqual(response.getStatus(), six.moves.http_client.CREATED)
    document_module = self.getDocumentModule()
    self.assertIn(filename, document_module.objectIds())
    self.assertEqual(document_module[filename].getPortalType(), 'Presentation')
    file_object.seek(0)
    self.assertEqual(document_module[filename].getData(), file_object.read())

  def test_GET_on_contributionTool(self):
    """Get a document through Contribution Tool.

    XXX not sure if this test is usefull as listing all Documents from ZODB
    can collapse the portal
    """
    # Create a new document via FTP/DAV
    path = self.portal.portal_contributions.getPath()
    filename = 'P-DMS-Presentation.3.Pages-001-en.odp'
    file_object = makeFileUpload(filename)
    response = self.publish('%s/%s' % (path, filename),
                            request_method='PUT',
                            stdin=file_object,
                            basic=self.authentication)

    self.assertEqual(response.getStatus(), six.moves.http_client.CREATED)
    self.tic()

    # check Document fetching
    document_module = self.getDocumentModule()
    document = document_module[filename]
    document_id = '%s-%s' % (document.getUid(), filename,)
    # This is HTTPServer.zhttp_server not HTTPServer.zwebdav_server
    # force usage of manage_FTPget like zwebdav_server does
    response = self.publish('%s/%s/manage_FTPget' % (path, document_id),
                            request_method='GET',
                            stdin=StringIO(),
                            basic=self.authentication)
    self.assertEqual(response.getStatus(), six.moves.http_client.OK)
    self.assertEqual(response.getBody(), document.getData(),
          'Error in getting data, get:%r' % response.getHeader('content-type'))

  def test_PUT_on_web_page(self):
    """Edit a web_page in webdav
    with encoded data in iso-8859-1
    """
    # Create a new document via FTP/DAV
    path = self.portal.portal_contributions.getPath()
    filename = 'my_document.html'
    response = self.publish('%s/%s' % (path, filename),
                            request_method='PUT',
                            basic=self.authentication)

    self.assertEqual(response.getStatus(), six.moves.http_client.CREATED)
    web_page_module = self.getWebPageModule()
    self.assertIn(filename, web_page_module.objectIds())
    self.assertEqual(web_page_module[filename].getPortalType(), 'Web Page')

    # Edit a new document via FTP/DAV
    text_content= """<html>
      <head>
        <meta http-equiv="Content-Type" content="text/html; charset=iso-8859-1">
      </head>
      <body>
        <p>Content edited through webdav in iso-8859-1</p>
        <p>éàèùêôîç</p>
      </body>
    </html>
    """
    iso_text_content = text_content.decode('utf-8').encode('iso-8859-1')
    path = web_page_module.getPath()
    for _ in xrange(2): # Run twice to check the code that compares
                        # old & new data when setting file attribute.
      response = self.publish('%s/%s' % (path, filename),
                              request_method='PUT',
                              stdin=StringIO(iso_text_content),
                              basic=self.authentication)
      self.assertEqual(response.getStatus(), six.moves.http_client.NO_CONTENT)
      self.assertEqual(web_page_module[filename].getData(), iso_text_content)
    # Convert to base format and run conversion into utf-8
    self.tic()
    # Content-Type header is replaced if sonversion encoding succeed
    new_text_content = text_content.replace('charset=iso-8859-1', 'charset=utf-8')
    self.assertEqual(web_page_module[filename].getTextContent(), new_text_content)

  def test_GET_on_document(self):
    """Get data from document in webdav
    """
    path = self.portal.portal_contributions.getPath()
    filename = 'P-DMS-Presentation.3.Pages-001-en.odp'
    file_object = makeFileUpload(filename)
    response = self.publish('%s/%s' % (path, filename),
                            request_method='PUT',
                            stdin=file_object,
                            basic=self.authentication)
    # Convert to base format and run conversion into utf-8
    self.tic()

    document_module = self.getDocumentModule()
    document = document_module[filename]

    # This is HTTPServer.zhttp_server not HTTPServer.zwebdav_server
    # force usage of manage_FTPget like zwebdav_server does
    response = self.publish(document.getPath()+'/manage_FTPget',
                            request_method='GET',
                            stdin=StringIO(),
                            basic=self.authentication)

    self.assertEqual(response.getStatus(), six.moves.http_client.OK)
    self.assertEqual(response.getBody(), document.getData(),
             'Error in getting data, get:%r' % response.getHeader('content-type'))

  def test_PROPFIND_on_document(self):
    """test Metadata extraction from webdav protocol
    """
    path = self.portal.portal_contributions.getPath()
    filename = 'P-DMS-Presentation.3.Pages-001-en.odp'
    file_object = makeFileUpload(filename)
    response = self.publish('%s/%s' % (path, filename),
                            request_method='PUT',
                            stdin=file_object,
                            basic=self.authentication)
    document_module = self.getDocumentModule()
    document = document_module[filename]

    # Do a PROPFIND on document, this needs to result in a 207
    response = self.publish(document.getPath(),
                            request_method='PROPFIND',
                            env={'HTTP_DEPTH': '0'},
                            stdin=StringIO(),
                            basic=self.authentication)

    self.assertEqual(response.getStatus(), six.moves.http_client.MULTI_STATUS)
    xml_metadata_string = response.getBody()
    xml_metadata = etree.fromstring(xml_metadata_string)
    self.assertEqual(xml_metadata.find('{DAV:}response/{DAV:}href').text,
                      document.getPath())
    self.assertEqual(xml_metadata.find(
                      '{DAV:}response/{DAV:}propstat/{DAV:}prop/'\
                      '{DAV:}getcontenttype').text,
                      document.getContentType())
    # Outputed string is not reproductable for comparaison.
    # So we need to parse the date and use the same format
    self.assertEqual(DateTime(xml_metadata.find('{DAV:}response/'\
                      '{DAV:}propstat/{DAV:}prop/{DAV:}getlastmodified')\
                      .text).ISO8601(),
                      DateTime(document._p_mtime).toZone('UTC').ISO8601())

  @expectedFailure
  def test_PROPFIND_on_document_bis(self):
    """same test than test_PROPFIND_on_document
    But with expected failure which is non blocking.
    """
    path = self.portal.portal_contributions.getPath()
    filename = 'P-DMS-Presentation.3.Pages-001-en.odp'
    file_object = makeFileUpload(filename)
    response = self.publish('%s/%s' % (path, filename),
                            request_method='PUT',
                            stdin=file_object,
                            basic=self.authentication)
    document_module = self.getDocumentModule()
    document = document_module[filename]

    # Do a PROPFIND on document, this needs to result in a 207
    response = self.publish(document.getPath(),
                            request_method='PROPFIND',
                            env={'HTTP_DEPTH': '0'},
                            stdin=StringIO(),
                            basic=self.authentication)

    self.assertEqual(response.getStatus(), six.moves.http_client.MULTI_STATUS)
    xml_metadata_string = response.getBody()
    xml_metadata = etree.fromstring(xml_metadata_string)
    self.assertEqual(xml_metadata.find(
           '{DAV:}response/{DAV:}propstat/{DAV:}prop/{DAV:}creationdate').text,
                      document.getCreationDate().HTML4())

def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestWebDavSupport))
  return suite
