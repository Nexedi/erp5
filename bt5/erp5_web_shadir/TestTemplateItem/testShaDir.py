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
import json
import transaction
from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from StringIO import StringIO
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

  def postInformation(self, key=None):
    """
      Post the information calling the Python Script.
      It simulates the real usage.
    """
    if key is None:
      key = self.key

    try:
      data_file = StringIO()
      data_file.write(self.data)
      data_file.seek(0)

      self.portal.changeSkin('SHADIR')
      path = self.shadir.getPath()
      response = self.publish('%s/%s' % (path, key),
                        request_method='PUT',
                        stdin=data_file,
                        basic='ERP5TypeTestCase:')
      self.stepTic()
      self.assertEqual(response.getStatus(), httplib.CREATED)
    finally:
      data_file.close()

  def getInformation(self, key=None):
    """
      Get the information calling the Python Script.
      It simulates the real usage.
    """
    if key is None:
      key = self.key

    self.portal.changeSkin('SHADIR')
    self.shadir.REQUEST.set('method', 'GET')
    return self.shadir.WebSection_getDocumentValue(key)

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
    self.postInformation()

    # Asserting Data Set
    data_set = self.portal.data_set_module.contentValues()[0]
    self.assertEquals(self.key, data_set.getReference())
    self.assertEquals('Published', data_set.getValidationStateTitle())

    # Asserting Document
    document = self.portal.document_module.contentValues()[0]
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

    document = self.getInformation()
    self.assertNotEquals(None, document)

    data = document.getData()
    information_list = json.loads(data)

    self.assertEquals(1, len(information_list))
    self.assertEquals(json.dumps(information_list[0]), self.data)

  def test_post_information_more_than_once(self):
    """
      Check if posting information is working.
    """
    self.assertEquals(0, len(self.portal.data_set_module))
    self.assertEquals(0, len(self.portal.document_module))

    self.postInformation()
    for x in xrange(10):
      self.postInformation()


    self.assertEquals(1, len(self.portal.data_set_module))
    data_set = self.portal.data_set_module.contentValues()[0]
    self.assertEquals(self.key, data_set.getReference())
    self.assertEquals('Published', data_set.getValidationStateTitle())

    self.assertEquals(11, len(self.portal.document_module))

  def test_get_information_for_single_data_set(self):
    """
      check if return the temp document with text content.
    """
    self.postInformation()

    document = self.getInformation()
    self.assertNotEquals(None, document)

    data = document.getData()
    information_list = json.loads(data)

    self.assertEquals(1, len(information_list))
    self.assertEquals(json.dumps(information_list[0]), self.data)

  def test_get_information_from_different_data_set(self):
    """
      POST information to /information and  to /information2
      It must create two Data Set and two Text documents.

      When the user retrieve the content of a given key,
      it must return only the Text document related to the key.

      This relation is controlled by Data Set object.
    """
    self.assertEquals(0, len(self.portal.data_set_module))
    self.assertEquals(0, len(self.portal.document_module))

    self.postInformation()
    self.assertEquals(1, len(self.portal.data_set_module))
    self.assertEquals(1, len(self.portal.document_module))

    self.postInformation(key='information2')
    self.assertEquals(2, len(self.portal.data_set_module))
    self.assertEquals(2, len(self.portal.document_module))

    document = self.getInformation()
    self.assertEquals(1, len(json.loads(document.getData())))

    document2 = self.getInformation('information2')
    self.assertEquals(1, len(json.loads(document2.getData())))

    self.postInformation()
    self.assertEquals(2, len(self.portal.data_set_module))
    self.assertEquals(3, len(self.portal.document_module))

    document3 = self.getInformation()
    self.assertEquals(2, len(json.loads(document3.getData())))
