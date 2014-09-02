##############################################################################
#
# Copyright (c) 2010 Nexedi SA and Contributors. All Rights Reserved.
#                     Lucas Carvalho <lucas@nexedi.com>
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


import unittest
from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase

class TestUrl(ERP5TypeTestCase):
  """
    Tests Url
  """

  def getBusinessTemplateList(self):
    return ('erp5_base',
            'erp5_web',
            'erp5_ingestion',
            'erp5_dms',)

  def test_document_asUrl(self):
    """
      This test should make sure that asURL should return the correct url.
    """
    portal = self.getPortalObject()
    url_crawler = portal.external_source_module.newContent(
                                                  portal_type='URL Crawler')

    url_protocol_list = ['http', 'https']

    for url_protocol in url_protocol_list:
      url_crawler.setUrlProtocol(url_protocol)
      self.tic()

      url_without_port = 'localhost/test_client'
      url_crawler.setUrlString(url_without_port)
      self.tic()
      self.assertEqual('%s://%s' % (url_protocol, url_without_port),
                                        url_crawler.asURL())

      full_url_without_port = '%s://localhost/test_client' % url_protocol
      url_crawler.setUrlString(full_url_without_port)
      self.tic()
      self.assertEqual(full_url_without_port, url_crawler.asURL())

      full_url_with_port = '%s://localhost:8191/test_client' % url_protocol
      url_crawler.setUrlString(full_url_with_port)
      self.tic()
      self.assertEqual(full_url_with_port, url_crawler.asURL())

      url_with_port = 'localhost:8191/test_client'
      url_crawler.setUrlString(url_with_port)
      self.tic()
      self.assertEqual('%s://%s' % (url_protocol, url_with_port),
                                                url_crawler.asURL())

      production_url = 'www.example.com/foo'
      url_crawler.setUrlString(production_url)
      self.tic()
      self.assertEqual('%s://%s' % (url_protocol, production_url),
                                                url_crawler.asURL())

      production_url_with_port = 'www.example.com:8191/foo'
      url_crawler.setUrlString(production_url_with_port)
      self.tic()
      self.assertEqual('%s://%s' % (url_protocol, production_url_with_port),
                                                url_crawler.asURL())

      production_url_with_protocol = '%s://www.example.com/foo' % url_protocol
      url_crawler.setUrlString(production_url_with_protocol)
      self.tic()
      self.assertEqual(production_url_with_protocol, url_crawler.asURL())

      production_url_with_port = '%s://www.example.com:8191/foo' % url_protocol
      url_crawler.setUrlString(production_url)
      self.tic()
      self.assertEqual('%s://%s' % (url_protocol, production_url),
                                                url_crawler.asURL())



def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestUrl))
  return suite
