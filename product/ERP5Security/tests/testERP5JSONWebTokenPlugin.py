# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2016 Nexedi SA and Contributors. All Rights Reserved.
#                    Cédric Le Ninivin <cedric.leninivin@nexedi.com>
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
import jwt
from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
import random
import StringIO
import transaction
import time
import unittest
from ZPublisher.HTTPRequest import HTTPRequest
from ZPublisher.HTTPResponse import HTTPResponse

class TestERP5JSONWebTokenPlugin(ERP5TypeTestCase):

  test_id = 'test_erp5_json_web_token_plugin'

  def getBusinessTemplateList(self):
    return (
      'erp5_full_text_mroonga_catalog',
      'erp5_core_proxy_field_legacy',
      'erp5_base',
      )

  def generateNewId(self):
    return str(self.portal.portal_ids.generateNewId(
         id_group=('test_erp5_json_web_token_plugin_id')))

  def afterSetUp(self):
    """
    This is ran before anything, used to set the environment
    """
    self.portal = self.getPortalObject()
    self.new_id = self.generateNewId()
    self._setupJSONWebTokenPLugin()
    transaction.commit()
    self.tic()

  def do_fake_request(self, request_method, headers={}):
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

  def _setupJSONWebTokenPLugin(self):
    pas = self.portal.acl_users
    access_extraction_list = [q for q in pas.objectValues() \
        if q.meta_type == 'ERP5 JSON Web Token Plugin']
    if len(access_extraction_list) == 0:
      dispacher = pas.manage_addProduct['ERP5Security']
      dispacher.addERP5JSONWebTokenPlugin(self.test_id)
      getattr(pas, self.test_id).manage_activateInterfaces(
        ('IExtractionPlugin', 'IAuthenticationPlugin'))
    elif len(access_extraction_list) == 1:
      self.test_id = access_extraction_list[0].getId()
    elif len(access_extraction_list) > 1:
      raise ValueError
    transaction.commit()

  def _createPerson(self, new_id, password=None):
    """Creates a person in person module, and returns the object, after
    indexing is done. """
    person_module = self.getPersonModule()
    person = person_module.newContent(portal_type='Person',
      reference='TESTP-' + new_id)
    if password:
      person.setPassword(password)
    person.newContent(portal_type = 'Assignment').open()
    transaction.commit()
    return person

  def test_working_authentication(self):
    """
    Test the normal authentication process for JWT Plugin
    Step 1: Login with password
    Step 2: Login with cookies provided by the response
    """
    password = "%s" % random.random()
    person = self.person = self._createPerson(
      self.new_id,
      password=password,
      )
    self.tic()
    request = self.do_fake_request(
      "GET",
      {"HTTP_AUTHORIZATION": "Basic " + base64.b64encode("%s:%s" % (
        person.getReference(), password))})
    ret = self.portal.acl_users[self.test_id].extractCredentials(request)
    self.assertEquals(ret,
      {
        'login': person.getReference(),
        'password': password,
        'remote_host': 'bobo.remote.host',
        'remote_address': '204.183.226.81 '
      }
    )
    ret = self.portal.acl_users["erp5_users"].authenticateCredentials(ret)
    self.assertEquals(ret, (person.getReference(), person.getReference()))
    self.portal.acl_users[self.test_id].updateCredentials(
      self.REQUEST,
      self.REQUEST.response,
      ret[0],
      password
      )
    response_cookie_dict = self.REQUEST.response.cookies
    erp5_jwt_cookie = response_cookie_dict.get('erp5_jwt')
    self.assertIsNotNone(erp5_jwt_cookie)
    self.assertTrue(erp5_jwt_cookie['http_only'])
    self.assertTrue(erp5_jwt_cookie['secure'])
    self.assertTrue(erp5_jwt_cookie['same_site'])
    request = self.do_fake_request("GET")
    request.cookies['erp5_jwt'] = erp5_jwt_cookie['value']
    ret = self.portal.acl_users[self.test_id].extractCredentials(request)
    self.assertEquals(ret,
      {
        'person_relative_url': person.getRelativeUrl(),
        'remote_host': 'bobo.remote.host',
        'remote_address': '204.183.226.81 '
      }
    )
    ret = self.portal.acl_users["erp5_users"].authenticateCredentials(ret)
    self.assertEquals(ret, (person.getReference(), person.getReference()))

  def test_invalid_signature(self):
    """
    Test authentication will fail if a wrong signature is provided in the token
      in the same site cookie
    """
    password = "%s" % random.random()
    person = self.person = self._createPerson(
      self.new_id,
      password=password,
      )
    self.tic()
    request = self.do_fake_request(
      "GET",
      {"HTTP_AUTHORIZATION": "Basic " + base64.b64encode("%s:%s" % (
        person.getReference(), password))})
    ret = self.portal.acl_users[self.test_id].extractCredentials(request)
    self.assertEquals(ret,
      {
        'login': person.getReference(),
        'password': password,
        'remote_host': 'bobo.remote.host',
        'remote_address': '204.183.226.81 '
      }
    )
    ret = self.portal.acl_users["erp5_users"].authenticateCredentials(ret)
    self.assertEquals(ret, (person.getReference(), person.getReference()))
    self.portal.acl_users[self.test_id].updateCredentials(
      self.REQUEST,
      self.REQUEST.response,
      ret[0],
      password
      )
    response_cookie_dict = self.REQUEST.response.cookies
    erp5_jwt_cookie = response_cookie_dict.get('erp5_jwt')
    request = self.do_fake_request("GET")
    request.cookies['erp5_jwt'] = erp5_jwt_cookie['value'] + "A"
    ret = self.portal.acl_users[self.test_id].extractCredentials(request)
    self.assertIsNone(ret)
    self.assertEquals(request.response.cookies['erp5_jwt']['value'], 'deleted')

  def test_origin_equal_base_url(self):
    """
    Test user is authenticated if same site cookie is valid and
      origin equal base url
    """
    password = "%s" % random.random()
    person = self.person = self._createPerson(
      self.new_id,
      password=password,
      )
    self.tic()
    origin = "https://www.example.com"
    self.portal.acl_users[self.test_id].updateCredentials(
      self.REQUEST,
      self.REQUEST.response,
      person.getReference(),
      password
      )
    response_cookie_dict = self.REQUEST.response.cookies
    erp5_jwt_cookie = response_cookie_dict.get('erp5_jwt')
    request = self.do_fake_request("GET")
    request.environ["ORIGIN"] = request.get("BASE0")
    request.cookies['erp5_jwt'] = erp5_jwt_cookie['value']
    ret = self.portal.acl_users[self.test_id].extractCredentials(request)
    self.assertEquals(ret,
      {
        'person_relative_url': person.getRelativeUrl(),
        'remote_host': 'bobo.remote.host',
        'remote_address': '204.183.226.81 '
      }
    )


  def test_valid_cors_domain(self):
    """
    Test user is authenticated if origin is in authorized cors domain list
      of a valid erp5 jwt cors cookie
    """
    password = "%s" % random.random()
    person = self.person = self._createPerson(
      self.new_id,
      password=password,
      )
    self.tic()
    origin = "https://www.example.com"
    self.REQUEST.form['new_cors_origin'] = origin
    self.portal.acl_users[self.test_id].updateCredentials(
      self.REQUEST,
      self.REQUEST.response,
      person.getReference(),
      password
      )
    response_cookie_dict = self.REQUEST.response.cookies
    erp5_cors_jwt_cookie = response_cookie_dict.get('erp5_cors_jwt')
    request = self.do_fake_request(
      "GET",
      {
        "ORIGIN": origin,
      }
    )
    request.cookies['erp5_cors_jwt'] = erp5_cors_jwt_cookie['value']
    ret = self.portal.acl_users[self.test_id].extractCredentials(request)
    self.assertEquals(ret,
      {
        'person_relative_url': person.getRelativeUrl(),
        'remote_host': 'bobo.remote.host',
        'remote_address': '204.183.226.81 '
      }
    )

  def test_invalid_cors_domain(self):
    """
    Test user is not authenticated if origin is not in authorized cors domain
      list of the erp5 jwt cors cookie
    """
    password = "%s" % random.random()
    person = self.person = self._createPerson(
      self.new_id,
      password=password,
      )
    self.tic()
    origin = "https://www.example.com"
    origin2 = "https://www.counter-exmaple.org"
    self.REQUEST.form['new_cors_origin'] = origin
    self.portal.acl_users[self.test_id].updateCredentials(
      self.REQUEST,
      self.REQUEST.response,
      person.getReference(),
      password
      )
    response_cookie_dict = self.REQUEST.response.cookies
    erp5_cors_jwt_cookie = response_cookie_dict.get('erp5_cors_jwt')
    request = self.do_fake_request(
      "GET",
      {
        "ORIGIN": origin2,
      }
    )
    request.cookies['erp5_cors_jwt'] = erp5_cors_jwt_cookie['value']
    ret = self.portal.acl_users[self.test_id].extractCredentials(request)
    self.assertEquals(ret,
      {
        'remote_host': 'bobo.remote.host',
        'remote_address': '204.183.226.81 '
      }
    )

  def test_valid_referer_domain(self):
    """
    Test user is authenticated if referer is in authorized cors domain list
      of a valid erp5 jwt cors cookie
    """
    password = "%s" % random.random()
    person = self.person = self._createPerson(
      self.new_id,
      password=password,
      )
    self.tic()
    origin = "https://www.example.com"
    self.REQUEST.form['new_cors_origin'] = origin
    self.portal.acl_users[self.test_id].updateCredentials(
      self.REQUEST,
      self.REQUEST.response,
      person.getReference(),
      password
      )
    response_cookie_dict = self.REQUEST.response.cookies
    erp5_cors_jwt_cookie = response_cookie_dict.get('erp5_cors_jwt')
    request = self.do_fake_request(
      "GET",
      {
        "REFERER": origin + "/couscous/erp5?foo=bar",
      }
    )
    request.cookies['erp5_cors_jwt'] = erp5_cors_jwt_cookie['value']
    ret = self.portal.acl_users[self.test_id].extractCredentials(request)
    self.assertEquals(ret,
      {
        'person_relative_url': person.getRelativeUrl(),
        'remote_host': 'bobo.remote.host',
        'remote_address': '204.183.226.81 '
      }
    )

  def test_invalid_referer_domain(self):
    """
    Test user is not authenticated if referer is not in authorized cors domain
      list of the erp5 jwt cors cookie
    """
    password = "%s" % random.random()
    person = self.person = self._createPerson(
      self.new_id,
      password=password,
      )
    self.tic()
    origin = "https://www.example.com"
    origin2 = "https://www.counter-exmaple.org"
    self.REQUEST.form['new_cors_origin'] = origin
    self.portal.acl_users[self.test_id].updateCredentials(
      self.REQUEST,
      self.REQUEST.response,
      person.getReference(),
      password
      )
    response_cookie_dict = self.REQUEST.response.cookies
    erp5_cors_jwt_cookie = response_cookie_dict.get('erp5_cors_jwt')
    request = self.do_fake_request(
      "GET",
      {
        "REFERER": origin2  + "/couscous/erp5?foo=bar",
      }
    )
    request.cookies['erp5_cors_jwt'] = erp5_cors_jwt_cookie['value']
    ret = self.portal.acl_users[self.test_id].extractCredentials(request)
    self.assertEquals(ret,
      {
        'remote_host': 'bobo.remote.host',
        'remote_address': '204.183.226.81 '
      }
    )

  def test_expiration_delay(self):
    """
    Test an expiration delay.
    """
    password = "%s" % random.random()
    person = self.person = self._createPerson(
      self.new_id,
      password=password,
      )
    self.tic()
    request = self.do_fake_request(
      "GET",
      {"HTTP_AUTHORIZATION": "Basic " + base64.b64encode("%s:%s" % (
        person.getReference(), password))})
    self.portal.acl_users[self.test_id].manage_setERP5JSONWebTokenPluginExtpirationDelay(2)
    ret = self.portal.acl_users[self.test_id].extractCredentials(request)
    self.portal.acl_users[self.test_id].updateCredentials(
      self.REQUEST,
      self.REQUEST.response,
      person.getReference(),
      password
      )
    response_cookie_dict = self.REQUEST.response.cookies
    erp5_jwt_cookie = response_cookie_dict.get('erp5_jwt')
    request = self.do_fake_request("GET")
    request.cookies['erp5_jwt'] = erp5_jwt_cookie['value']
    ret = self.portal.acl_users[self.test_id].extractCredentials(request)
    self.assertEquals(ret,
      {
        'person_relative_url': person.getRelativeUrl(),
        'remote_host': 'bobo.remote.host',
        'remote_address': '204.183.226.81 '
      }
    )
    time.sleep(3)
    request = self.do_fake_request("GET")
    request.cookies['erp5_jwt'] = erp5_jwt_cookie['value']
    ret = self.portal.acl_users[self.test_id].extractCredentials(request)
    self.assertIsNone(ret)

  def test_expiration_delay_deactivated_by_default(self):
    """
    Test an expiration delay is deactivated by default
    """
    password = "%s" % random.random()
    person = self.person = self._createPerson(
      self.new_id,
      password=password,
      )
    self.tic()
    request = self.do_fake_request(
      "GET",
      {"HTTP_AUTHORIZATION": "Basic " + base64.b64encode("%s:%s" % (
        person.getReference(), password))})
    ret = self.portal.acl_users[self.test_id].extractCredentials(request)
    self.portal.acl_users[self.test_id].updateCredentials(
      self.REQUEST,
      self.REQUEST.response,
      person.getReference(),
      password
      )
    response_cookie_dict = self.REQUEST.response.cookies
    erp5_jwt_cookie = response_cookie_dict.get('erp5_jwt')
    decoded_value = jwt.decode(erp5_jwt_cookie["value"], verify=False)
    self.assertTrue("exp" not in decoded_value)

  def test_expiration_delay_deactivated_when_set_to_0(self):
    """
    Test an expiration delay is deactivated by default
    """
    password = "%s" % random.random()
    person = self.person = self._createPerson(
      self.new_id,
      password=password,
      )
    self.tic()
    self.portal.acl_users[self.test_id].manage_setERP5JSONWebTokenPluginExtpirationDelay(2)
    request = self.do_fake_request(
      "GET",
      {"HTTP_AUTHORIZATION": "Basic " + base64.b64encode("%s:%s" % (
        person.getReference(), password))})
    ret = self.portal.acl_users[self.test_id].extractCredentials(request)
    self.portal.acl_users[self.test_id].updateCredentials(
      self.REQUEST,
      self.REQUEST.response,
      person.getReference(),
      password
      )
    response_cookie_dict = self.REQUEST.response.cookies
    erp5_jwt_cookie = response_cookie_dict.get('erp5_jwt')
    decoded_value = jwt.decode(erp5_jwt_cookie["value"], verify=False)
    self.assertTrue("exp" in decoded_value)
    self.portal.acl_users[self.test_id].manage_setERP5JSONWebTokenPluginExtpirationDelay(0)
    request = self.do_fake_request(
      "GET",
      {"HTTP_AUTHORIZATION": "Basic " + base64.b64encode("%s:%s" % (
        person.getReference(), password))})
    ret = self.portal.acl_users[self.test_id].extractCredentials(request)
    self.portal.acl_users[self.test_id].updateCredentials(
      self.REQUEST,
      self.REQUEST.response,
      person.getReference(),
      password
      )
    response_cookie_dict = self.REQUEST.response.cookies
    erp5_jwt_cookie = response_cookie_dict.get('erp5_jwt')
    decoded_value = jwt.decode(erp5_jwt_cookie["value"], verify=False)
    self.assertTrue("exp" not in decoded_value)

  def test_update_password_tid_invalidate_token(self):
    """
    Test update Password TID invalide JWT
    """
    password = "%s" % random.random()
    person = self.person = self._createPerson(
      self.new_id,
      password=password,
      )
    self.tic()
    self.portal.acl_users[self.test_id].manage_setERP5JSONWebTokenPluginExtpirationDelay(2)
    request = self.do_fake_request(
      "GET",
      {"HTTP_AUTHORIZATION": "Basic " + base64.b64encode("%s:%s" % (
        person.getReference(), password))})
    ret = self.portal.acl_users[self.test_id].extractCredentials(request)
    self.portal.acl_users[self.test_id].updateCredentials(
      self.REQUEST,
      self.REQUEST.response,
      person.getReference(),
      password
      )
    response_cookie_dict = self.REQUEST.response.cookies
    erp5_jwt_cookie = response_cookie_dict.get('erp5_jwt')
    request = self.do_fake_request("GET")
    request.cookies['erp5_jwt'] = erp5_jwt_cookie['value']
    ret = self.portal.acl_users[self.test_id].extractCredentials(request)
    self.assertEquals(ret,
      {
        'person_relative_url': person.getRelativeUrl(),
        'remote_host': 'bobo.remote.host',
        'remote_address': '204.183.226.81 '
      }
    )
    person.serializePassword()
    self.commit()
    request = self.do_fake_request("GET")
    request.cookies['erp5_jwt'] = erp5_jwt_cookie['value']
    ret = self.portal.acl_users[self.test_id].extractCredentials(request)
    self.assertEquals(ret,
      {
        'remote_host': 'bobo.remote.host',
        'remote_address': '204.183.226.81 '
      }
    )


def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestERP5JSONWebTokenPlugin))
  return suite
