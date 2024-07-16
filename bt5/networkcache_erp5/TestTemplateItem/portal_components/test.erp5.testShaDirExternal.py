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


import base64
import json
import os
import six.moves.http_client
from DateTime import DateTime
from Products.ERP5Type.tests.ERP5TypeLiveTestCase import ERP5TypeTestCase
from erp5.component.test.ShaDirMixin import ShaDirMixin
from erp5.component.test.ShaSecurityMixin import ShaSecurityMixin


class TestShaDirExternal(ShaDirMixin, ShaSecurityMixin, ERP5TypeTestCase):
  """
    ShaDir - HTTP Information Cache server
    We must simulate the real usage of ShaDir using httplib.
  """

  def getTitle(self):
    """
      Return the title of the current test set.
    """
    return "SHADIR External - Real Usage Of ShaDir"

  def afterSetUp(self):
    """
      Initialize the ERP5 site.
    """
    self.group = 'shadir'
    ShaDirMixin.afterSetUp(self)
    ShaSecurityMixin.afterSetUp(self)

    # Define POST headers with Authentication
    self.content_type =  'application/json'
    authentication_string = 'lucas:lucas'
    base64string = base64.encodestring(authentication_string).strip()
    self.header_dict = {'Authorization': 'Basic %s' % base64string,
                        'Content-Type': self.content_type}

    # HTTP Connection properties
    self.host = self.portal.REQUEST.get('SERVER_NAME')
    self.port = self.portal.REQUEST.get('SERVER_PORT')
    self.path = os.path.join(self.shadir.getPath(), self.key)

  def test_external_post(self):
    """
      Test the external usage to POST information
    """
    now = DateTime()
    connection = six.moves.http_client.HTTPConnection('%s:%s' % (self.host, self.port))
    try:
      connection.request('PUT', self.path, self.data, self.header_dict)
      result = connection.getresponse()
      self.tic()
      data = result.read()
    finally:
      connection.close()
    self.assertEqual('', data)
    self.assertEqual(201, result.status)

    # Check Data Set
    data_set = self.portal.portal_catalog.getResultValue(
                              portal_type='Data Set',
                              reference=self.key)
    self.assertNotEqual(None, data_set)
    self.assertEqual('Published', data_set.getValidationStateTitle())

    # Check Document
    document = self.portal.portal_catalog.getResultValue(portal_type='File',
                                                reference=self.sha512sum,
                                                creation_date=' >= "%s"' % now)
    self.assertNotEqual(None, document)
    self.assertEqual(self.data, document.getData())
    self.assertEqual(str(self.expiration_date),
                               str(document.getExpirationDate()))
    self.assertEqual(data_set, document.getFollowUpValue())
    self.assertEqual('File', document.getPortalType())
    self.assertEqual('Published', document.getValidationStateTitle())

  def test_external_get(self, annonymous=False):
    """
      Test the external usage to retrive the information
    """
    self.test_external_post()
    header_dict = {}
    if not annonymous:
      header_dict = self.header_dict

    connection = six.moves.http_client.HTTPConnection('%s:%s' % (self.host, self.port))
    try:
      connection.request('GET', self.path, headers=header_dict)
      result = connection.getresponse()
      data = result.read()
    finally:
      connection.close()
    self.assertEqual(json.dumps([json.loads(self.data)]), data)
    self.assertEqual(200, result.status)
    self.assertEqual(self.content_type, result.getheader("content-type"))

  def test_external_get_anonymous(self):
    """
      Test the external usage to retrive information
      accessing as Anonymous User.
    """
    self.test_external_get(annonymous=True)

  def test_external_post_anonymous(self):
    """
    """
    connection = six.moves.http_client.HTTPConnection('%s:%s' % (self.host, self.port))
    header_dict = {'Content-Type': self.content_type}
    try:
      connection.request('PUT', self.path, self.data, header_dict)
      result = connection.getresponse()
      self.tic()
    finally:
      connection.close()
    self.assertEqual(302, result.status)

  def test_external_post_with_wrong_data(self):
    # Removing a required property
    data = json.loads(self.data)
    data[0] = json.loads(data[0])
    del data[0]['sha512']
    data[0] = json.dumps(data[0])
    data = json.dumps(data)

    connection = six.moves.http_client.HTTPConnection('%s:%s' % (self.host, self.port))
    try:
      connection.request('PUT', self.path, data, self.header_dict)
      result = connection.getresponse()
      self.tic()
      data = result.read()
    finally:
      connection.close()
    self.assertEqual(400, result.status)
    self.assertEqual('text/html; charset=utf-8',
                                         result.getheader("content-type"))
