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


import httplib
import urlparse
import json
import transaction
import random
from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from ShaDirMixin import ShaDirMixin


class TestShaDir(ShaDirMixin, ERP5TypeTestCase):
  """
    ShaDir - HTTP Information Cache server
  """

  def getTitle(self):
    """
      Return the title of the current test set.
    """
    return "SHADIR - HTTP Information Cache Server"

  def postInformation(self, key=None, data=None):
    """
      Post the information calling the Python Script.
      It simulates the real usage.
    """
    parsed = urlparse.urlparse(self.shadir_url)
    connection = httplib.HTTPConnection(parsed.hostname, parsed.port)
    try:
      connection.request('PUT', '/'.join([parsed.path, key or self.key]),
        data or self.data, self.header_dict)
      result = connection.getresponse()
      data = result.read()
    finally:
      connection.close()
    return result.status, data

  def getInformation(self, key=None):
    """
      Get the information calling the Python Script.
      It simulates the real usage.
    """
    parsed = urlparse.urlparse(self.shadir_url)
    connection = httplib.HTTPConnection(parsed.hostname, parsed.port)
    try:
      connection.request('GET', '/'.join([parsed.path, key or self.key]),
        self.data, self.header_dict)
      result = connection.getresponse()
      data = result.read()
    finally:
      connection.close()
    return result.status, data

  def beforeTearDown(self):
    """
      Clear everything for next test.
    """
    for module in ('data_set_module',
                   'document_module',):
      folder = self.portal[module]
      folder.manage_delObjects(list(folder.objectIds()))
    self.portal.portal_caches.clearAllCache()
    transaction.commit()
    self.tic()

  def test_post_information(self):
    """
      Check if posting information is working.
    """
    result, data = self.postInformation()

    self.assertEqual(result, httplib.CREATED)
    self.assertEqual(data, '')

    transaction.commit()
    self.tic()

    # Asserting Data Set
    data_set = self.portal.portal_catalog.getResultValue(
      reference=self.key)
    self.assertEquals(self.key, data_set.getReference())
    self.assertEquals('published', data_set.getValidationState())

    # Asserting Document
    document = self.portal.portal_catalog.getResultValue(
      reference=self.sha512sum)
    self.assertEquals(self.sha512sum, document.getTitle())
    self.assertEquals(self.sha512sum, document.getReference())
    self.assertEquals(self.data, document.getData())
    self.assertEquals(data_set, document.getFollowUpValue())
    self.assertEquals(str(self.expiration_date),
                                    str(document.getExpirationDate()))
    self.assertEquals('application/json', document.getContentType())
    self.assertEquals('Published', document.getValidationStateTitle())

  def test_get_information(self):
    """
      check if return the temp document with text content.
    """
    self.postInformation()

    transaction.commit()
    self.tic()

    result, data = self.getInformation()
    self.assertEqual(result, httplib.OK)

    information_list = json.loads(data)

    self.assertEquals(1, len(information_list))
    self.assertEquals(json.dumps(information_list[0]), self.data)

  def test_post_information_more_than_once(self):
    """
      Check if posting information is working.
    """
    result, data = self.postInformation()

    self.assertEqual(result, httplib.CREATED)
    self.assertEqual(data, '')
    transaction.commit()
    self.tic()

    result, data = self.postInformation()

    self.assertEqual(result, httplib.CREATED)
    self.assertEqual(data, '')
    transaction.commit()
    self.tic()

    self.assertEqual(1, self.portal.portal_catalog.countResults(
      reference=self.key)[0][0])
    data_set = self.portal.portal_catalog.getResultValue(
      reference=self.key)
    self.assertEqual(self.key, data_set.getReference())
    self.assertEqual('published', data_set.getValidationState())

    document_list = data_set.getFollowUpRelatedValueList()

    self.assertEqual([self.sha512sum, self.sha512sum], [q.getReference() for q \
        in document_list])
    self.assertEqual(sorted(['published', 'archived']), sorted([
        q.getValidationState() for q in document_list]))

  def test_get_information_for_single_data_set(self):
    """
      check if return the temp document with text content.
    """
    self.postInformation()

    transaction.commit()
    self.tic()
    result, data = self.getInformation()
    self.assertEqual(result, httplib.OK)
    information_list = json.loads(data)

    self.assertEquals(1, len(information_list))
    self.assertEquals(json.dumps(information_list[0]), self.data)

  def test_get_information_from_different_data_set(self):
    """
      POST information with two different keys
      It must create two Data Set and two Text documents.

      When the user retrieve the content of a given key,
      it must return only the Text document related to the key.

      This relation is controlled by Data Set object.
    """
    self.postInformation()

    transaction.commit()
    self.tic()

    urlmd5_2 = 'anotherurlmd5' + str(random.random())
    sha512_2 = 'anothersha512_2' + str(random.random())
    key_2 = 'another_key' + str(random.random())
    data_list_2 = [{'file': self.file_name,
                      'urlmd5': urlmd5_2,
                      'sha512': sha512_2,
                      'creation_date': str(self.creation_date),
                      'expiration_date': str(self.expiration_date),
                      'distribution': self.distribution,
                      'architecture': self.architecture},
                      "User SIGNATURE goes here."]
    data_2 = json.dumps(data_list_2)
    result, data = self.postInformation(key_2, data_2)
    self.assertEqual(result, httplib.CREATED)

    transaction.commit()
    self.tic()

    self.assertEquals(2, len(self.portal.data_set_module))
    self.assertEquals(2, len(self.portal.document_module))

    result, document = self.getInformation()
    self.assertEquals(1, len(json.loads(document)))

    result, document2 = self.getInformation(key_2)
    self.assertEquals(1, len(json.loads(document2)))

    result, data = self.postInformation()
    self.assertEqual(result, httplib.CREATED)

    transaction.commit()
    self.tic()
    self.assertEquals(2, len(self.portal.data_set_module))
    self.assertEquals(3, len(self.portal.document_module))

    result, document3 = self.getInformation()
    self.assertEquals(2, len(json.loads(document3)))
