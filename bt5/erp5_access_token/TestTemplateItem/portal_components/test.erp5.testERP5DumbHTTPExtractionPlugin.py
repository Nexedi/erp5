# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2015 Nexedi SA and Contributors. All Rights Reserved.
#                    Tristan Cavelier <tristan.cavelier@nexedi.com>
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

from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from ZPublisher.HTTPRequest import HTTPRequest
from ZPublisher.HTTPResponse import HTTPResponse
from Products.ERP5Security.ERP5DumbHTTPExtractionPlugin import ERP5DumbHTTPExtractionPlugin
import base64
import StringIO

class TestERP5DumbHTTPExtractionPlugin(ERP5TypeTestCase):

  test_id = 'test_erp5_dumb_http_extraction'

  def getBusinessTemplateList(self):
    return ('erp5_base',)

  def generateNewId(self):
    return str(self.portal.portal_ids.generateNewId(
         id_group=('erp5_dumb_http_test_id')))

  def afterSetUp(self):
    """
    This is ran before anything, used to set the environment
    """
    self.new_id = self.generateNewId()
    self._setupDumbHTTPExtraction()
    self.tic()

  def do_fake_request(self, request_method, headers=None):
    if headers is None:
      headers = {}
    __version__ = "0.1"
    env={}
    env['SERVER_NAME']='bobo.server'
    env['SERVER_PORT']='80'
    env['REQUEST_METHOD']=request_method
    env['REMOTE_ADDR']='204.183.226.81 '
    env['REMOTE_HOST']='bobo.remote.host'
    env['HTTP_USER_AGENT']='Bobo/%s' % __version__
    env['HTTP_HOST']='127.0.0.1'
    env['SERVER_SOFTWARE']='Bobo/%s' % __version__
    env['SERVER_PROTOCOL']='HTTP/1.0 '
    env['HTTP_ACCEPT']='image/gif, image/x-xbitmap, image/jpeg, */* '
    env['SERVER_HOSTNAME']='bobo.server.host'
    env['GATEWAY_INTERFACE']='CGI/1.1 '
    env['SCRIPT_NAME']='Main'
    env.update(headers)
    return HTTPRequest(StringIO.StringIO(), env, HTTPResponse())

  def _setupDumbHTTPExtraction(self):
    pas = self.portal.acl_users
    access_extraction_list = [q for q in pas.objectValues() \
        if q.meta_type == 'ERP5 Dumb HTTP Extraction Plugin']
    if len(access_extraction_list) == 0:
      dispacher = pas.manage_addProduct['ERP5Security']
      dispacher.addERP5DumbHTTPExtractionPlugin(self.test_id)
      getattr(pas, self.test_id).manage_activateInterfaces(
        ('IExtractionPlugin',))
    elif len(access_extraction_list) == 1:
      self.test_id = access_extraction_list[0].getId()
    elif len(access_extraction_list) > 1:
      raise ValueError
    self.commit()

  def _createPerson(self, new_id, password=None):
    """Creates a person in person module, and returns the object, after
    indexing is done. """
    person_module = self.getPersonModule()
    person = person_module.newContent(portal_type='Person',
      reference='TESTP-' + new_id)
    if password:
      person.setPassword(password)
    person.newContent(portal_type = 'Assignment').open()
    self.tic()
    return person

  def test_working_authentication(self):
    self._createPerson(self.new_id, "test")
    request = self.do_fake_request("GET", {"HTTP_AUTHORIZATION": "Basic " + base64.b64encode("%s:test" % self.new_id)})
    ret = ERP5DumbHTTPExtractionPlugin("default_extraction").extractCredentials(request)
    self.assertEqual(ret, {'login': self.new_id, 'password': 'test', 'remote_host': 'bobo.remote.host', 'remote_address': '204.183.226.81 '})
