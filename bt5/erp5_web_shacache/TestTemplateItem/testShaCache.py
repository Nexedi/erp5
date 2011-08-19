# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2011 Nexedi SA and Contributors. All Rights Reserved.
#                    Lucas Carvalho <lucas@nexedi.com>
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


import transaction
import httplib
import urlparse
from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from ShaCacheMixin import ShaCacheMixin


class TestShaCache(ShaCacheMixin, ERP5TypeTestCase):
  """
    ShaCache - HTTP File Cache server
  """

  def getTitle(self):
    """
      Return the title of the current test set.
    """
    return "SHACACHE - HTTP File Cache Server"

  def postFile(self, key=None):
    """
      Post the file
    """
    parsed = urlparse.urlparse(self.shacache_url)
    connection = httplib.HTTPConnection(parsed.hostname, parsed.port)
    try:
      connection.request('POST', parsed.path, self.data, self.header_dict)
      result = connection.getresponse()
      data = result.read()
    finally:
      connection.close()
    return result.status, data

  def getFile(self, key=None):
    """
      Get the file calling the Python Script.
      It simulates the real usage.
    """
    if key is None:
      key = self.key

    parsed = urlparse.urlparse(self.shacache_url)
    connection = httplib.HTTPConnection(parsed.hostname, parsed.port)
    try:
      connection.request('GET', '/'.join([parsed.path, key]), None,
        self.header_dict)
      result = connection.getresponse()
      data = result.read()
    finally:
      connection.close()
    return result.status, data

  def test_put_file(self):
    """
      Check if the PUT method is creating an object.
    """
    result, data = self.postFile()
    self.assertEqual(result, httplib.CREATED)
    self.assertEqual(data, self.key)

    transaction.commit()
    self.tic()

    document = self.portal.portal_catalog.getResultValue(reference=self.key)
    self.assertNotEqual(None, document)
    self.assertEquals(self.key, document.getTitle())
    self.assertEquals(self.key, document.getReference())
    self.assertEquals(self.data, document.getData())
    self.assertEquals('application/octet-stream', document.getContentType())
    self.assertEquals('Published', document.getValidationStateTitle())

  def test_get_file(self):
    """
      Check if the file returned is the correct.
    """
    result, data = self.postFile()
    self.assertEqual(result, httplib.CREATED)
    self.assertEqual(data, self.key)

    transaction.commit()
    self.tic()

    document = self.portal.portal_catalog.getResultValue(reference=self.key)
    self.assertNotEqual(None, document)

    result, data = self.getFile()
    self.assertEqual(result, httplib.OK)
    self.assertEquals(data, self.data)

  def test_put_file_twice(self):
    """
      Check if is allowed to put the same file twice.
    """
    self.postFile()
    transaction.commit()
    self.tic()
    document = self.portal.portal_catalog.getResultValue(reference=self.key)
    self.assertEquals('Published', document.getValidationStateTitle())

    self.postFile()
    transaction.commit()
    self.tic()
    self.assertEquals(2, self.portal.portal_catalog.countResults(
      reference=self.key)[0][0])

    document2 = self.portal.portal_catalog.getResultValue(reference=self.key,
      sort_on=(('uid', 'ASC'),))
    self.assertEquals('Published', document2.getValidationStateTitle())
    self.assertEquals('archived', document.getValidationState())


