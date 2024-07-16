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
import six.moves.http_client
from unittest import expectedFailure
from DateTime import DateTime
from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from erp5.component.test.ShaCacheMixin import ShaCacheMixin
from erp5.component.test.ShaSecurityMixin import ShaSecurityMixin

class TestShaCacheExternal(ShaCacheMixin, ShaSecurityMixin, ERP5TypeTestCase):
  """
    ShaCache - HTTP File Cache server
    We must simulate the real usage of ShaCache using httplib.
  """

  def getTitle(self):
    """
      Return the title of the current test set.
    """
    return "SHACACHE External - Real Usage Of ShaCache"

  def afterSetUp(self):
    """
      Initialize the ERP5 site.
    """
    self.expected_content_type = 'application/octet-stream'
    self.group = 'shacache'
    ShaCacheMixin.afterSetUp(self)
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
    self.path = self.shacache.getPath()

  def test_external_post(self):
    """
      Test the external usage to POST information
    """
    now = DateTime()
    connection = six.moves.http_client.HTTPConnection('%s:%s' % (self.host, self.port))
    try:
      connection.request('POST', self.path, self.data, self.header_dict)
      result = connection.getresponse()
      self.tic()
      data = result.read()
    finally:
      connection.close()
    self.assertEqual(self.key, data.decode())
    self.assertEqual(six.moves.http_client.CREATED, result.status)

    # Check Document
    document = self.portal.portal_catalog.getResultValue(portal_type='File',
                                                  reference=self.key,
                                                  creation_date=' >= "%s"' % now)
    self.assertNotEqual(None, document)
    self.assertEqual(self.data, document.getData())
    self.assertEqual('File', document.getPortalType())
    self.assertEqual('Published', document.getValidationStateTitle())
    self.assertEqual(self.expected_content_type, document.getContentType())

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
      connection.request('GET', '/'.join([self.path, self.key]),
        headers=header_dict)
      result = connection.getresponse()
      data = result.read()
    finally:
      connection.close()
    self.assertEqual(self.data, data)
    self.assertEqual(six.moves.http_client.OK, result.status)
    self.assertEqual(self.expected_content_type,
                           result.getheader("content-type"))

  def test_external_get_anonymous(self):
    """
      Test the external usage to retrive information
      accessing as Anonymous User.
    """
    self.test_external_get(annonymous=True)

  @expectedFailure
  def test_external_post_anonymous(self):
    """
      Anonymous should not be able to POST a file.
    """
    connection = six.moves.http_client.HTTPConnection('%s:%s' % (self.host, self.port))
    header_dict = {'Content-Type': self.content_type}
    try:
      connection.request('POST', self.path, self.data, header_dict)
      result = connection.getresponse()
      self.tic()
    finally:
      connection.close()
    # For now ERP5 returns httplib.FOUND which is wrong reply in case of trying
    # to POST resource while begin not authorised
    # One of UNAUTHORIZED or FORBIDDEN shall be returned
    # Ref: http://www.w3.org/Protocols/rfc2616/rfc2616-sec10.html#sec10.4
    # self.assertEqual(httplib.UNAUTHORIZED, result.status)
    # FORBIDDEN seems more suitable for RESTful server...
    self.assertEqual(six.moves.http_client.FORBIDDEN, result.status)
