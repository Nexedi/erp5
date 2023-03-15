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

import six.moves.http_client
import six.moves.urllib.parse
import hashlib
import json
import random
from base64 import b64encode
from unittest import expectedFailure
from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from erp5.component.test.ShaDirMixin import ShaDirMixin
from Products.ERP5Type.Utils import bytes2str


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
    parsed = six.moves.urllib.parse.urlparse(self.shadir_url)
    connection = six.moves.http_client.HTTPConnection(parsed.hostname, parsed.port)
    try:
      connection.request('PUT', '/'.join([parsed.path, key or self.key]),
        data or self.data, self.header_dict)
      result = connection.getresponse()
      data = result.read()
    finally:
      connection.close()
    self.assertEqual(result.status, six.moves.http_client.CREATED)
    self.assertEqual(data, b'')

  def getInformation(self, key=None):
    """
      Get the information calling the Python Script.
      It simulates the real usage.
    """
    parsed = six.moves.urllib.parse.urlparse(self.shadir_url)
    connection = six.moves.http_client.HTTPConnection(parsed.hostname, parsed.port)
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
    self.tic()

  def test_post_information(self):
    """
      Check if posting information is working.
    """
    self.postInformation()
    self.tic()

    # Asserting Data Set
    data_set = self.portal.portal_catalog.getResultValue(
      reference=self.key)
    self.assertEqual(self.key, data_set.getReference())
    self.assertNotEqual(self.key, data_set.getId())
    self.assertEqual('published', data_set.getValidationState())
    self.assertEqual(len(self.portal.data_set_module.contentValues()), 1)

    # Asserting Document
    document = self.portal.portal_catalog.getResultValue(
      reference=self.sha512sum)
    self.assertEqual(self.sha512sum, document.getTitle())
    self.assertEqual(self.sha512sum, document.getReference())
    self.assertNotEqual(self.sha512sum, document.getId())
    self.assertEqual(self.data, document.getData())
    self.assertEqual(data_set, document.getFollowUpValue())
    self.assertEqual(str(self.expiration_date),
                                    str(document.getExpirationDate()))
    self.assertEqual('application/json', document.getContentType())
    self.assertEqual('Published', document.getValidationStateTitle())
    self.assertEqual(len(self.portal.document_module.contentValues()), 1)

  def test_get_information(self):
    """
      check if return the temp document with text content.
    """
    self.postInformation()

    self.tic()

    result, data = self.getInformation()
    self.assertEqual(result, six.moves.http_client.OK)

    information_list = json.loads(data)

    self.assertEqual(1, len(information_list))
    self.assertEqual(json.dumps(information_list[0]), bytes2str(self.data))

  def test_post_information_more_than_once(self):
    """
      Check if posting information is working.
    """
    self.postInformation()
    self.tic()

    self.postInformation()
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

    result, data = self.getInformation()
    self.assertEqual(result, six.moves.http_client.OK)
    information_list = json.loads(data)

    self.assertEqual(1, len(information_list))
    self.assertEqual(json.dumps(information_list[0]), bytes2str(self.data))

  def test_post_information_more_than_once_no_tic(self):
    """
      Check if posting information is working.
    """
    self.postInformation()
    self.commit()

    self.postInformation()
    self.tic()

    expectedFailure(self.assertEqual)(1,
      self.portal.portal_catalog.countResults(reference=self.key)[0][0])
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
    self.tic()

    result, data = self.getInformation()
    self.assertEqual(result, six.moves.http_client.OK)
    information_list = json.loads(data)

    self.assertEqual(1, len(information_list))
    self.assertEqual(json.dumps(information_list[0]), bytes2str(self.data))

  def test_get_information_from_different_data_set(self):
    """
      POST information with two different keys
      It must create two Data Set and two Text documents.

      When the user retrieve the content of a given key,
      it must return only the Text document related to the key.

      This relation is controlled by Data Set object.
    """
    self.postInformation()
    self.tic()

    sha512_2 = hashlib.sha512(str(random.random()).encode()).hexdigest()
    key_2 = 'another_key' + str(random.random())
    data_list_2 = [json.dumps({
                      'sha512': sha512_2,
                      'creation_date': str(self.creation_date),
                      'expiration_date': str(self.expiration_date),
                      'distribution': self.distribution,
                      'architecture': self.architecture}),
                      b64encode(b"User SIGNATURE goes here.").decode()]
    data_2 = json.dumps(data_list_2)
    self.postInformation(key_2, data_2)
    self.tic()

    self.assertEqual(2, len(self.portal.data_set_module))
    self.assertEqual(2, len(self.portal.document_module))

    result, document = self.getInformation()
    self.assertEqual(1, len(json.loads(document)))

    result, document2 = self.getInformation(key_2)
    self.assertEqual(1, len(json.loads(document2)))

    self.postInformation()
    self.tic()
    self.assertEqual(2, len(self.portal.data_set_module))
    self.assertEqual(3, len(self.portal.document_module))

    result, document3 = self.getInformation()
    self.assertEqual(1, len(json.loads(document3)))


  def test_VirtualFolder_key(self):
    module = self.portal.newContent(portal_type='Folder', id='test_virtual_folder_%s' % random.random())
    # WebSite is a VirtualFolder
    vf1 = module.newContent(portal_type='Web Site')
    vf2 = module.newContent(portal_type='Web Site')
    obj_id = "test_obj_%s" % random.random()
    obj = vf1.newContent(portal_type='Web Section', id=obj_id)
    self.assertEqual(obj, vf1._getOb(obj_id))
    self.assertIsNone(vf2._getOb(obj_id, default=None))

  def test_post_information_with_other_documents(self):
    """
      Check if code works when there are unrelated
      shacache documents.
    """
    person = self.portal.person_module.newContent(portal_type="Person")
    doc = self.portal.document_module.newContent(
            portal_type="File",
            reference="F-TESTSHADIR",
            version="001",
            language="en",
            follow_up_value=person,
            data=b"FILEDATA")
    doc.publish()

    self.tic()
    self.test_post_information_more_than_once()
