# -*- coding: utf-8 -*-
# Copyright (c) 2002-2015 Nexedi SA and Contributors. All Rights Reserved.
import transaction
from zExceptions import Unauthorized
from Products.ERP5Type.tests.utils import createZODBPythonScript
from unittest import skip
from functools import wraps

from ZPublisher.HTTPRequest import HTTPRequest
from ZPublisher.HTTPResponse import HTTPResponse

import StringIO
import json
import urllib

def changeSkin(skin_name):
  def decorator(func):
    def wrapped(self, *args, **kwargs):
      default_skin = self.portal.portal_skins.default_skin
      self.portal.portal_skins.changeSkin(skin_name)
      self.app.REQUEST.set('portal_skin', skin_name)
      try:
        v = func(self, *args, **kwargs)
      finally:
        self.portal.portal_skins.changeSkin(default_skin)
        self.app.REQUEST.set('portal_skin', default_skin)
      return v
    return wrapped
  return decorator

def simulate(script_id, params_string, code_string):
  def upperWrap(f):
    @wraps(f)
    def decorated(self, *args, **kw):
      if script_id in self.portal.portal_skins.custom.objectIds():
        raise ValueError('Precondition failed: %s exists in custom' % script_id)
      createZODBPythonScript(self.portal.portal_skins.custom,
                          script_id, params_string, code_string)
      transaction.commit()
      try:
        result = f(self, *args, **kw)
      finally:
        if script_id in self.portal.portal_skins.custom.objectIds():
          self.portal.portal_skins.custom.manage_delObjects(script_id)
        transaction.commit()
      return result
    return decorated
  return upperWrap

def do_fake_request(request_method, headers=None):
  __version__ = "0.1"
  if (headers is None):
    headers = {}
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

from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase

#####################################################
# Base_getRequestHeader
#####################################################
class ERP5HALJSONStyleSkinsMixin(ERP5TypeTestCase):
  def afterSetUp(self):
    self.login()

  def beforeTearDown(self):
    transaction.abort()
    
  def generateNewId(self):
    return "%sö" % self.portal.portal_ids.generateNewId(
                                     id_group=('erp5_hal_json_style_test'))

  def _makeDocument(self):
    new_id = self.generateNewId()
    foo = self.portal.foo_module.newContent(portal_type="Foo")
    foo.edit(
      title="live_test_%s" % new_id,
      reference="live_test_%s" % new_id
    )
    return foo
  
class TestBase_getRequestHeader(ERP5HALJSONStyleSkinsMixin):
  @changeSkin('Hal')
  def test_getRequestHeader_REQUEST_disallowed(self):
    self.assertRaises(
      Unauthorized,
      self.portal.Base_getRequestHeader,
      "foo",
      REQUEST={})

  @changeSkin('Hal')
  def test_getRequestHeader_key_error(self):
    self.assertEquals(
        self.portal.Base_getRequestHeader('foo'),
        None
        )

  @changeSkin('Hal')
  def test_getRequestHeader_default_value(self):
    self.assertEquals(
        self.portal.Base_getRequestHeader('foo', default='bar'),
        'bar'
        )

  @skip('TODO')
  def test_getRequestHeader_matching_key(self):
    pass

#####################################################
# Base_getRequestUrl
#####################################################
class TestBase_getRequestUrl(ERP5HALJSONStyleSkinsMixin):
  @changeSkin('Hal')
  def test_getRequestUrl_REQUEST_disallowed(self):
    self.assertRaises(
      Unauthorized,
      self.portal.Base_getRequestUrl,
      REQUEST={})

  @skip('TODO')
  def test_getRequestUrl_matching_key(self):
    pass

#####################################################
# Base_getRequestBody
#####################################################
class TestBase_getRequestBody(ERP5HALJSONStyleSkinsMixin):
  @changeSkin('Hal')
  def test_getRequestBody_REQUEST_disallowed(self):
    self.assertRaises(
      Unauthorized,
      self.portal.Base_getRequestBody,
      REQUEST={})

  @skip('TODO')
  def test_getRequestBody_matching_key(self):
    pass

#####################################################
# Base_handleAcceptHeader
#####################################################
class TestBase_handleAcceptHeader(ERP5HALJSONStyleSkinsMixin):
  @changeSkin('Hal')
  def test_handleAcceptHeader_REQUEST_disallowed(self):
    self.assertRaises(
      Unauthorized,
      self.portal.Base_handleAcceptHeader,
      [],
      REQUEST={})

  @simulate('Base_getRequestHeader', '*args, **kwargs', 'return "*/*"')
  @changeSkin('Hal')
  def test_handleAcceptHeader_star_accept(self):
    self.assertEquals(
        self.portal.Base_handleAcceptHeader(['application/vnd+test',
                                             'application/vnd+test2']),
        'application/vnd+test'
        )

  @simulate('Base_getRequestHeader', '*args, **kwargs',
            'return "application/vnd+2test"')
  @changeSkin('Hal')
  def test_handleAcceptHeader_matching_type(self):
    self.assertEquals(
        self.portal.Base_handleAcceptHeader(['application/vnd+test',
                                             'application/vnd+2test']),
        'application/vnd+2test'
        )

  @simulate('Base_getRequestHeader', '*args, **kwargs',
            'return "application/vnd+2test"')
  @changeSkin('Hal')
  def test_handleAcceptHeader_non_matching_type(self):
    self.assertEquals(
        self.portal.Base_handleAcceptHeader(['application/vnd+test']),
        None
        )

class TestERP5Document_getHateoas_general(ERP5HALJSONStyleSkinsMixin):

  @simulate('Base_getRequestHeader', '*args, **kwargs',
            'return "application/vnd+bar"')
  @changeSkin('Hal')
  def test_getHateoas_wrong_ACCEPT(self):
    document = self._makeDocument()
    fake_request = do_fake_request("GET")
    result = document.ERP5Document_getHateoas(REQUEST=fake_request)
    self.assertEquals(fake_request.RESPONSE.status, 406)
    self.assertEquals(result, "")

  @skip('TODO')
  def test_getHateoas_drop_restricted(self):
    pass

  @simulate('Base_getRequestHeader', '*args, **kwargs',
            'return "application/hal+json"')
  @changeSkin('Hal')
  def test_getHateoas_unsupported_mode(self):
    fake_request = do_fake_request("GET")
    self.assertRaises(
      NotImplementedError,
      self.portal.ERP5Document_getHateoas,
      REQUEST=fake_request,
      mode="bar")

class TestERP5Document_getHateoas_mode_root(ERP5HALJSONStyleSkinsMixin):

  @simulate('Base_getRequestHeader', '*args, **kwargs',
            'return "application/hal+json"')
  @changeSkin('Hal')
  def test_getHateoasDocument_bad_method(self):
    document = self._makeDocument()
    fake_request = do_fake_request("POST")
    result = document.ERP5Document_getHateoas(REQUEST=fake_request)
    self.assertEquals(fake_request.RESPONSE.status, 405)
    self.assertEquals(result, "")

  @simulate('Base_getRequestUrl', '*args, **kwargs',
      'return "http://example.org/bar"')
  @simulate('Base_getRequestHeader', '*args, **kwargs',
            'return "application/hal+json"')
  @changeSkin('Hal')
  def test_getHateoasDocument_result(self):
    document = self._makeDocument()
    parent = document.getParentValue()
    fake_request = do_fake_request("GET")
    result = document.ERP5Document_getHateoas(REQUEST=fake_request)
    self.assertEquals(fake_request.RESPONSE.status, 200)
    self.assertEquals(fake_request.RESPONSE.getHeader('Content-Type'),
      "application/hal+json"
    )
    result_dict = json.loads(result)
    self.assertEqual(result_dict['_links']['self'], {"href": "http://example.org/bar"})

    self.assertEqual(result_dict['_links']['parent'],
                    {"href": "urn:jio:get:%s" % parent.getRelativeUrl(), "name": parent.getTitle()})

    self.assertEqual(result_dict['_links']['view'][0]['href'],
                     "%s/ERP5Document_getHateoas?mode=traverse&relative_url=%s&view=view" % (
                       self.portal.absolute_url(),
                       urllib.quote_plus(document.getRelativeUrl())))
    self.assertEqual(result_dict['_links']['view'][0]['title'], "View")
    self.assertEqual(result_dict['_links']['view'][0]['name'], "view")

    self.assertEqual(result_dict['_links']['action_object_view'][0]['href'],
                     "%s/ERP5Document_getHateoas?mode=traverse&relative_url=%s&view=view" % (
                       self.portal.absolute_url(),
                       urllib.quote_plus(document.getRelativeUrl())))
    self.assertEqual(result_dict['_links']['action_object_view'][0]['title'], "View")
    self.assertEqual(result_dict['_links']['action_object_view'][0]['name'], "view")

    self.assertEqual(result_dict['_links']['action_workflow'][0]['href'],
                     "%s/ERP5Document_getHateoas?mode=traverse&relative_url=%s&view=custom_action_no_dialog" % (
                       self.portal.absolute_url(),
                       urllib.quote_plus(document.getRelativeUrl())))
    self.assertEqual(result_dict['_links']['action_workflow'][0]['title'], "Custom Action No Dialog")
    self.assertEqual(result_dict['_links']['action_workflow'][0]['name'], "custom_action_no_dialog")

    self.assertEqual(result_dict['_links']['portal']['href'], 'urn:jio:get:%s' % document.getPortalObject().getId())
    self.assertEqual(result_dict['_links']['portal']['name'], document.getPortalObject().getTitle())

    # XXX Not so usefull results
    self.assertEqual(result_dict['_links']['site_root']['href'], 'urn:jio:get:')
    self.assertEqual(result_dict['_links']['site_root']['name'], document.getPortalObject().getTitle())

    self.assertEqual(result_dict['_links']['action_object_new_content_action']['href'],
                     "%s/ERP5Document_getHateoas?mode=traverse&relative_url=%s&view=create_a_document" % (
                       self.portal.absolute_url(),
                       urllib.quote_plus(document.getRelativeUrl())))
    self.assertEqual(result_dict['_links']['action_object_new_content_action']['title'], "Create a Document")
    self.assertEqual(result_dict['_links']['action_object_new_content_action']['name'], "create_a_document")

    self.assertEqual(result_dict['_links']['type']['href'], 'urn:jio:get:portal_types/%s' % document.getPortalType())
    self.assertEqual(result_dict['_links']['type']['name'], document.getPortalType())

    self.assertEqual(result_dict['title'].encode("UTF-8"), document.getTitle())
    self.assertEqual(result_dict['_debug'], "root")

  @simulate('Base_getRequestUrl', '*args, **kwargs',
      'return "http://example.org/bar"')
  @simulate('Base_getRequestHeader', '*args, **kwargs',
            'return "application/hal+json"')
  @changeSkin('Hal')
  def test_getHateoasWebSite_result(self):
    document = self.portal.web_site_module.hateoas
    parent = document.getParentValue()
    fake_request = do_fake_request("GET")
    result = document.ERP5Document_getHateoas(REQUEST=fake_request)
    self.assertEquals(fake_request.RESPONSE.status, 200)
    self.assertEquals(fake_request.RESPONSE.getHeader('Content-Type'),
      "application/hal+json"
    )
    result_dict = json.loads(result)
    self.assertEqual(result_dict['_links']['self'], {"href": "http://example.org/bar"})

    self.assertEqual(result_dict['_links']['parent'],
                    {"href": "urn:jio:get:%s" % parent.getRelativeUrl(), "name": parent.getTitle()})

    self.assertEqual(result_dict['_links']['view'][0]['href'],
                     "%s/web_site_module/hateoas/ERP5Document_getHateoas?mode=traverse&relative_url=%s&view=view" % (
                       self.portal.absolute_url(),
                       urllib.quote_plus(document.getRelativeUrl())))
    self.assertEqual(result_dict['_links']['view'][0]['title'], "View")
    self.assertEqual(result_dict['_links']['view'][0]['name'], "view")

    self.assertEqual(result_dict['_links']['action_object_view'][0]['href'],
                     "%s/web_site_module/hateoas/ERP5Document_getHateoas?mode=traverse&relative_url=%s&view=view" % (
                       self.portal.absolute_url(),
                       urllib.quote_plus(document.getRelativeUrl())))
    self.assertEqual(result_dict['_links']['action_object_view'][0]['title'], "View")
    self.assertEqual(result_dict['_links']['action_object_view'][0]['name'], "view")

    self.assertEqual(result_dict['_links']['action_workflow'][0]['href'],
                     "%s/web_site_module/hateoas/ERP5Document_getHateoas?mode=traverse&relative_url=%s&view=embed_action" % (
                       self.portal.absolute_url(),
                       urllib.quote_plus(document.getRelativeUrl())))
    self.assertEqual(result_dict['_links']['action_workflow'][0]['title'], "Embed")
    self.assertEqual(result_dict['_links']['action_workflow'][0]['name'], "embed_action")

    self.assertEqual(result_dict['_links']['portal']['href'], 'urn:jio:get:%s' % document.getPortalObject().getId())
    self.assertEqual(result_dict['_links']['portal']['name'], document.getPortalObject().getTitle())

    self.assertEqual(result_dict['_links']['site_root']['href'], 'urn:jio:get:web_site_module/hateoas')
    self.assertEqual(result_dict['_links']['site_root']['name'], document.getTitle())

    self.assertEqual(result_dict['_links']['action_object_new_content_action']['href'],
                     "%s/web_site_module/hateoas/ERP5Document_getHateoas?mode=traverse&relative_url=%s&view=create_a_document" % (
                       self.portal.absolute_url(),
                       urllib.quote_plus(document.getRelativeUrl())))
    self.assertEqual(result_dict['_links']['action_object_new_content_action']['title'], "Create a Document")
    self.assertEqual(result_dict['_links']['action_object_new_content_action']['name'], "create_a_document")

    self.assertEqual(result_dict['_links']['type']['href'], 'urn:jio:get:portal_types/%s' % document.getPortalType())
    self.assertEqual(result_dict['_links']['type']['name'], document.getPortalType())

    self.assertEqual(result_dict['_links']['raw_search']['href'],
                     "%s/web_site_module/hateoas/ERP5Document_getHateoas?mode=search{&query,select_list*,limit*}" % self.portal.absolute_url())
    self.assertEqual(result_dict['_links']['raw_search']['templated'], True)
    self.assertEqual(result_dict['_links']['raw_search']['name'], "Raw Search")

    self.assertEqual(result_dict['_links']['traverse']['href'],
                     "%s/web_site_module/hateoas/ERP5Document_getHateoas?mode=traverse{&relative_url,view}" % self.portal.absolute_url())
    self.assertEqual(result_dict['_links']['traverse']['templated'], True)
    self.assertEqual(result_dict['_links']['traverse']['name'], "Traverse")

    self.assertEqual(result_dict['title'].encode("UTF-8"), document.getTitle())
    self.assertEqual(result_dict['default_view'], "view")
    self.assertEqual(result_dict['_debug'], "root")

    # XXX Check 'me' links


class TestERP5Document_getHateoas_mode_traverse(ERP5HALJSONStyleSkinsMixin):

  @simulate('Base_getRequestHeader', '*args, **kwargs',
            'return "application/hal+json"')
  @changeSkin('Hal')
  def test_getHateoasDocument_bad_method(self):
    document = self._makeDocument()
    fake_request = do_fake_request("POST")
    result = self.portal.web_site_module.hateoas.ERP5Document_getHateoas(REQUEST=fake_request, mode="traverse", relative_url=document.getRelativeUrl())
    self.assertEquals(fake_request.RESPONSE.status, 405)
    self.assertEquals(result, "")

  @simulate('Base_getRequestUrl', '*args, **kwargs',
      'return "http://example.org/bar"')
  @simulate('Base_getRequestHeader', '*args, **kwargs',
            'return "application/hal+json"')
  @changeSkin('Hal')
  def test_getHateoasDocument_no_view(self):
    document = self._makeDocument()
    parent = document.getParentValue()
    fake_request = do_fake_request("GET")
    result = self.portal.web_site_module.hateoas.ERP5Document_getHateoas(REQUEST=fake_request, mode="traverse", relative_url=document.getRelativeUrl())
    self.assertEquals(fake_request.RESPONSE.status, 200)
    self.assertEquals(fake_request.RESPONSE.getHeader('Content-Type'),
      "application/hal+json"
    )
    result_dict = json.loads(result)
    self.assertEqual(result_dict['_links']['self'], {"href": "http://example.org/bar"})

    self.assertEqual(result_dict['_links']['parent'],
                    {"href": "urn:jio:get:%s" % parent.getRelativeUrl(), "name": parent.getTitle()})

    self.assertEqual(result_dict['_links']['view'][0]['href'],
                     "%s/web_site_module/hateoas/ERP5Document_getHateoas?mode=traverse&relative_url=%s&view=view" % (
                       self.portal.absolute_url(),
                       urllib.quote_plus(document.getRelativeUrl())))
    self.assertEqual(result_dict['_links']['view'][0]['title'], "View")
    self.assertEqual(result_dict['_links']['view'][0]['name'], "view")

    self.assertEqual(result_dict['_links']['action_object_view'][0]['href'],
                     "%s/web_site_module/hateoas/ERP5Document_getHateoas?mode=traverse&relative_url=%s&view=view" % (
                       self.portal.absolute_url(),
                       urllib.quote_plus(document.getRelativeUrl())))
    self.assertEqual(result_dict['_links']['action_object_view'][0]['title'], "View")
    self.assertEqual(result_dict['_links']['action_object_view'][0]['name'], "view")

    self.assertEqual(result_dict['_links']['action_workflow'][0]['href'],
                     "%s/web_site_module/hateoas/ERP5Document_getHateoas?mode=traverse&relative_url=%s&view=custom_action_no_dialog" % (
                       self.portal.absolute_url(),
                       urllib.quote_plus(document.getRelativeUrl())))
    self.assertEqual(result_dict['_links']['action_workflow'][0]['title'], "Custom Action No Dialog")
    self.assertEqual(result_dict['_links']['action_workflow'][0]['name'], "custom_action_no_dialog")

    self.assertEqual(result_dict['_links']['portal']['href'], 'urn:jio:get:%s' % document.getPortalObject().getId())
    self.assertEqual(result_dict['_links']['portal']['name'], document.getPortalObject().getTitle())

    self.assertEqual(result_dict['_links']['site_root']['href'], 'urn:jio:get:web_site_module/hateoas')
    self.assertEqual(result_dict['_links']['site_root']['name'], self.portal.web_site_module.hateoas.getTitle())

    self.assertEqual(result_dict['_links']['action_object_new_content_action']['href'],
                     "%s/web_site_module/hateoas/ERP5Document_getHateoas?mode=traverse&relative_url=%s&view=create_a_document" % (
                       self.portal.absolute_url(),
                       urllib.quote_plus(document.getRelativeUrl())))
    self.assertEqual(result_dict['_links']['action_object_new_content_action']['title'], "Create a Document")
    self.assertEqual(result_dict['_links']['action_object_new_content_action']['name'], "create_a_document")

    self.assertEqual(result_dict['_links']['type']['href'], 'urn:jio:get:portal_types/%s' % document.getPortalType())
    self.assertEqual(result_dict['_links']['type']['name'], document.getPortalType())

    self.assertEqual(result_dict['title'].encode("UTF-8"), document.getTitle())
    self.assertEqual(result_dict['_debug'], "traverse")

  @simulate('Base_getRequestUrl', '*args, **kwargs',
      'return "http://example.org/bar"')
  @simulate('Base_getRequestHeader', '*args, **kwargs',
            'return "application/hal+json"')
  @changeSkin('Hal')
  def test_getHateoasDocument_default_view(self):
    document = self._makeDocument()
    parent = document.getParentValue()
    fake_request = do_fake_request("GET")
    result = self.portal.web_site_module.hateoas.ERP5Document_getHateoas(REQUEST=fake_request, mode="traverse", relative_url=document.getRelativeUrl(), view="view")
    self.assertEquals(fake_request.RESPONSE.status, 200)
    self.assertEquals(fake_request.RESPONSE.getHeader('Content-Type'),
      "application/hal+json"
    )
    result_dict = json.loads(result)
    self.assertEqual(result_dict['_links']['self'], {"href": "http://example.org/bar"})

    self.assertEqual(result_dict['_links']['parent'],
                    {"href": "urn:jio:get:%s" % parent.getRelativeUrl(), "name": parent.getTitle()})

    self.assertEqual(result_dict['_links']['view'][0]['href'],
                     "%s/web_site_module/hateoas/ERP5Document_getHateoas?mode=traverse&relative_url=%s&view=view" % (
                       self.portal.absolute_url(),
                       urllib.quote_plus(document.getRelativeUrl())))
    self.assertEqual(result_dict['_links']['view'][0]['title'], "View")
    self.assertEqual(result_dict['_links']['view'][0]['name'], "view")

    self.assertEqual(result_dict['_links']['action_object_view'][0]['href'],
                     "%s/web_site_module/hateoas/ERP5Document_getHateoas?mode=traverse&relative_url=%s&view=view" % (
                       self.portal.absolute_url(),
                       urllib.quote_plus(document.getRelativeUrl())))
    self.assertEqual(result_dict['_links']['action_object_view'][0]['title'], "View")
    self.assertEqual(result_dict['_links']['action_object_view'][0]['name'], "view")

    self.assertEqual(result_dict['_links']['action_workflow'][0]['href'],
                     "%s/web_site_module/hateoas/ERP5Document_getHateoas?mode=traverse&relative_url=%s&view=custom_action_no_dialog" % (
                       self.portal.absolute_url(),
                       urllib.quote_plus(document.getRelativeUrl())))
    self.assertEqual(result_dict['_links']['action_workflow'][0]['title'], "Custom Action No Dialog")
    self.assertEqual(result_dict['_links']['action_workflow'][0]['name'], "custom_action_no_dialog")

    self.assertEqual(result_dict['_links']['portal']['href'], 'urn:jio:get:%s' % document.getPortalObject().getId())
    self.assertEqual(result_dict['_links']['portal']['name'], document.getPortalObject().getTitle())

    self.assertEqual(result_dict['_links']['site_root']['href'], 'urn:jio:get:web_site_module/hateoas')
    self.assertEqual(result_dict['_links']['site_root']['name'], self.portal.web_site_module.hateoas.getTitle())

    self.assertEqual(result_dict['_links']['action_object_new_content_action']['href'],
                     "%s/web_site_module/hateoas/ERP5Document_getHateoas?mode=traverse&relative_url=%s&view=create_a_document" % (
                       self.portal.absolute_url(),
                       urllib.quote_plus(document.getRelativeUrl())))
    self.assertEqual(result_dict['_links']['action_object_new_content_action']['title'], "Create a Document")
    self.assertEqual(result_dict['_links']['action_object_new_content_action']['name'], "create_a_document")

    self.assertEqual(result_dict['_links']['type']['href'], 'urn:jio:get:portal_types/%s' % document.getPortalType())
    self.assertEqual(result_dict['_links']['type']['name'], document.getPortalType())

    self.assertEqual(result_dict['title'].encode("UTF-8"), document.getTitle())
    self.assertEqual(result_dict['_debug'], "traverse")

    # Check embedded form rendering
    self.assertEqual(result_dict['_embedded']['_view']['form_id']['default'], 'Foo_view')
    self.assertEqual(result_dict['_embedded']['_view']['form_id']['editable'], 0)
    self.assertEqual(result_dict['_embedded']['_view']['form_id']['hidden'], 1)
    self.assertEqual(result_dict['_embedded']['_view']['form_id']['key'], 'form_id')
    self.assertEqual(result_dict['_embedded']['_view']['form_id']['required'], 1)
    self.assertEqual(result_dict['_embedded']['_view']['form_id']['type'], 'StringField')

    self.assertEqual(result_dict['_embedded']['_view']['my_id']['default'], document.getId())
    self.assertEqual(result_dict['_embedded']['_view']['my_id']['editable'], 1)
    self.assertEqual(result_dict['_embedded']['_view']['my_id']['hidden'], 0)
    self.assertEqual(result_dict['_embedded']['_view']['my_id']['key'], 'field_my_id')
    self.assertEqual(result_dict['_embedded']['_view']['my_id']['required'], 1)
    self.assertEqual(result_dict['_embedded']['_view']['my_id']['type'], 'StringField')
    self.assertEqual(result_dict['_embedded']['_view']['my_id']['title'], 'ID')

    self.assertEqual(result_dict['_embedded']['_view']['_links']['traversed_document']['href'], 'urn:jio:get:%s' % document.getRelativeUrl())
    self.assertEqual(result_dict['_embedded']['_view']['_links']['traversed_document']['name'], document.getRelativeUrl())
    self.assertEqual(result_dict['_embedded']['_view']['_links']['traversed_document']['title'], document.getTitle().decode("UTF-8"))

    self.assertEqual(result_dict['_embedded']['_view']['_links']['self']['href'], "%s/%s/Foo_view" % (
                                                                                    self.portal.absolute_url(),
                                                                                    document.getRelativeUrl()))

    self.assertEqual(result_dict['_embedded']['_view']['_links']['form_definition']['href'], 'urn:jio:get:portal_skins/erp5_ui_test/Foo_view')
    self.assertEqual(result_dict['_embedded']['_view']['_links']['form_definition']['name'], 'Foo_view')

    self.assertEqual(result_dict['_embedded']['_view']['_actions']['put']['href'], '%s/web_site_module/hateoas/%s/Base_edit' % (
                                                                                     self.portal.absolute_url(),
                                                                                     document.getRelativeUrl()))
    self.assertEqual(result_dict['_embedded']['_view']['_actions']['put']['method'], 'POST')


  @simulate('Base_getRequestUrl', '*args, **kwargs',
      'return "http://example.org/bar"')
  @simulate('Base_getRequestHeader', '*args, **kwargs',
            'return "application/hal+json"')
  @changeSkin('Hal')
  def test_getHateoasForm_no_view(self):
    fake_request = do_fake_request("GET")
    result = self.portal.web_site_module.hateoas.ERP5Document_getHateoas(REQUEST=fake_request, mode="traverse", relative_url="portal_skins/erp5_ui_test/Foo_view")
    self.assertEquals(fake_request.RESPONSE.status, 200)
    self.assertEquals(fake_request.RESPONSE.getHeader('Content-Type'),
      "application/hal+json"
    )
    result_dict = json.loads(result)
    self.assertEqual(result_dict['_links']['self'], {"href": "http://example.org/bar"})

    self.assertEqual(result_dict['_links']['parent'],
                    {"href": "urn:jio:get:", "name": self.portal.getTitle()})

#    self.assertEqual(result_dict['_links']['view'][0]['href'],
#                     "%s/web_site_module/hateoas/ERP5Document_getHateoas?mode=traverse&relative_url=%s&view=consistency" % (
#                       self.portal.absolute_url(),
#                       urllib.quote_plus("portal_skins/erp5_ui_test/Foo_view")))
#    self.assertEqual(result_dict['_links']['view'][0]['title'], "Consistency")
#    self.assertEqual(result_dict['_links']['view'][0]['name'], "consistency")

#    self.assertEqual(result_dict['_links']['action_object_view'][0]['href'],
#                     "%s/web_site_module/hateoas/ERP5Document_getHateoas?mode=traverse&relative_url=%s&view=consistency" % (
#                       self.portal.absolute_url(),
#                       urllib.quote_plus("portal_skins/erp5_ui_test/Foo_view")))
#    self.assertEqual(result_dict['_links']['action_object_view'][0]['title'], "Consistency")
#    self.assertEqual(result_dict['_links']['action_object_view'][0]['name'], "consistency")

    self.assertEqual(result_dict['_links']['portal']['href'], 'urn:jio:get:%s' % self.portal.getId())
    self.assertEqual(result_dict['_links']['portal']['name'], self.portal.getTitle())

    self.assertEqual(result_dict['_links']['site_root']['href'], 'urn:jio:get:web_site_module/hateoas')
    self.assertEqual(result_dict['_links']['site_root']['name'], self.portal.web_site_module.hateoas.getTitle())

    self.assertEqual(result_dict['_links']['type']['href'], 'urn:jio:get:portal_types/ERP5 Form')
    self.assertEqual(result_dict['_links']['type']['name'], 'ERP5 Form')

    self.assertEqual(result_dict['title'], 'Foo')
    self.assertEqual(result_dict['pt'], 'form_view')
    self.assertEqual(result_dict['action'], 'Base_edit')
    self.assertEqual(result_dict['group_list'][0][0], 'left')
    self.assertEqual(result_dict['group_list'][0][1][0], ['my_id', {'meta_type': 'StringField'}])
    self.assertEqual(result_dict['_debug'], "traverse")

class TestERP5Document_getHateoas_mode_search(ERP5HALJSONStyleSkinsMixin):

  @simulate('Base_getRequestHeader', '*args, **kwargs',
            'return "application/hal+json"')
  @changeSkin('Hal')
  def test_getHateoasDocument_bad_method(self):
    fake_request = do_fake_request("POST")
    result = self.portal.web_site_module.hateoas.ERP5Document_getHateoas(REQUEST=fake_request, mode="search")
    self.assertEquals(fake_request.RESPONSE.status, 405)
    self.assertEquals(result, "")

  @simulate('Base_getRequestUrl', '*args, **kwargs',
      'return "http://example.org/bar"')
  @simulate('Base_getRequestHeader', '*args, **kwargs',
            'return "application/hal+json"')
  @changeSkin('Hal')
  def test_getHateoas_no_param(self):
    fake_request = do_fake_request("GET")
    result = self.portal.web_site_module.hateoas.ERP5Document_getHateoas(REQUEST=fake_request, mode="search")
    self.assertEquals(fake_request.RESPONSE.status, 200)
    self.assertEquals(fake_request.RESPONSE.getHeader('Content-Type'),
      "application/hal+json"
    )
    result_dict = json.loads(result)
    self.assertEqual(result_dict['_links']['self'], {"href": "http://example.org/bar"})

    self.assertEqual(result_dict['_links']['portal']['href'], 'urn:jio:get:%s' % self.portal.getId())
    self.assertEqual(result_dict['_links']['portal']['name'], self.portal.getTitle())

    self.assertEqual(result_dict['_links']['site_root']['href'], 'urn:jio:get:web_site_module/hateoas')
    self.assertEqual(result_dict['_links']['site_root']['name'], self.portal.web_site_module.hateoas.getTitle())

    self.assertEqual(result_dict['_debug'], "search")
    self.assertEqual(result_dict['_limit'], 10)
    self.assertEqual(result_dict['_query'], None)
    self.assertEqual(result_dict['_select_list'], [])

    self.assertEqual(len(result_dict['_embedded']['contents']), 10)
    self.assertEqual(result_dict['_embedded']['contents'][0]["_links"]["self"]["href"][:12], "urn:jio:get:")

  @simulate('Base_getRequestUrl', '*args, **kwargs',
      'return "http://example.org/bar"')
  @simulate('Base_getRequestHeader', '*args, **kwargs',
            'return "application/hal+json"')
  @changeSkin('Hal')
  def test_getHateoas_limit_param(self):
    fake_request = do_fake_request("GET")
    result = self.portal.web_site_module.hateoas.ERP5Document_getHateoas(REQUEST=fake_request, mode="search", limit=1)
    self.assertEquals(fake_request.RESPONSE.status, 200)
    self.assertEquals(fake_request.RESPONSE.getHeader('Content-Type'),
      "application/hal+json"
    )
    result_dict = json.loads(result)
    self.assertEqual(result_dict['_links']['self'], {"href": "http://example.org/bar"})

    self.assertEqual(result_dict['_debug'], "search")
    self.assertEqual(result_dict['_limit'], 1)
    self.assertEqual(result_dict['_query'], None)
    self.assertEqual(result_dict['_select_list'], [])

    self.assertEqual(len(result_dict['_embedded']['contents']), 1)
    self.assertEqual(result_dict['_embedded']['contents'][0]["_links"]["self"]["href"][:12], "urn:jio:get:")

    # self.assertEqual(result_dict, {}, json.dumps(result_dict, indent=2))


  @simulate('Base_getRequestUrl', '*args, **kwargs',
      'return "http://example.org/bar"')
  @simulate('Base_getRequestHeader', '*args, **kwargs',
            'return "application/hal+json"')
  @changeSkin('Hal')
  def test_getHateoas_select_list_param(self):
    fake_request = do_fake_request("GET")
    result = self.portal.web_site_module.hateoas.ERP5Document_getHateoas(REQUEST=fake_request, mode="search", select_list=["id", "relative_url"])
    self.assertEquals(fake_request.RESPONSE.status, 200)
    self.assertEquals(fake_request.RESPONSE.getHeader('Content-Type'),
      "application/hal+json"
    )
    result_dict = json.loads(result)
    self.assertEqual(result_dict['_links']['self'], {"href": "http://example.org/bar"})

    self.assertEqual(result_dict['_debug'], "search")
    self.assertEqual(result_dict['_limit'], 10)
    self.assertEqual(result_dict['_query'], None)
    self.assertEqual(result_dict['_select_list'], ["id", "relative_url"])

    self.assertEqual(len(result_dict['_embedded']['contents']), 10)
    relative_url = result_dict['_embedded']['contents'][0]["relative_url"]
    self.assertTrue(str(relative_url).endswith(result_dict['_embedded']['contents'][0]["id"]))
    self.assertEqual(result_dict['_embedded']['contents'][0]["_links"]["self"]["href"], "urn:jio:get:%s" % relative_url)

  @simulate('Base_getRequestUrl', '*args, **kwargs',
      'return "http://example.org/bar"')
  @simulate('Base_getRequestHeader', '*args, **kwargs',
            'return "application/hal+json"')
  @changeSkin('Hal')
  def test_getHateoas_query_param(self):
    fake_request = do_fake_request("GET")
    result = self.portal.web_site_module.hateoas.ERP5Document_getHateoas(REQUEST=fake_request, mode="search", query="ANIMPOSSIBLECOUSCOUSVALUEFOOTOFINDINDATA")
    self.assertEquals(fake_request.RESPONSE.status, 200)
    self.assertEquals(fake_request.RESPONSE.getHeader('Content-Type'),
      "application/hal+json"
    )
    result_dict = json.loads(result)
    self.assertEqual(result_dict['_links']['self'], {"href": "http://example.org/bar"})

    self.assertEqual(result_dict['_debug'], "search")
    self.assertEqual(result_dict['_limit'], 10)
    self.assertEqual(result_dict['_query'], "ANIMPOSSIBLECOUSCOUSVALUEFOOTOFINDINDATA")
    self.assertEqual(result_dict['_select_list'], [])

    self.assertEqual(len(result_dict['_embedded']['contents']), 0)


class TestERP5Document_getHateoas_mode_bulk(ERP5HALJSONStyleSkinsMixin):

  @simulate('Base_getRequestHeader', '*args, **kwargs',
            'return "application/hal+json"')
  @changeSkin('Hal')
  def test_getHateoasBulk_bad_method(self):
    fake_request = do_fake_request("GET")
    result = self.portal.web_site_module.hateoas.ERP5Document_getHateoas(REQUEST=fake_request, mode="bulk")
    self.assertEquals(fake_request.RESPONSE.status, 405)
    self.assertEquals(result, "")

  @simulate('Base_getRequestUrl', '*args, **kwargs',
      'return "http://example.org/bar"')
  @simulate('Base_getRequestHeader', '*args, **kwargs',
            'return "application/hal+json"')
  @changeSkin('Hal')
  def test_getHateoasBulk_default_view(self):
    document = self._makeDocument()
    parent = document.getParentValue()
    fake_request = do_fake_request("POST")
    result = self.portal.web_site_module.hateoas.ERP5Document_getHateoas(
      REQUEST=fake_request,
      mode="bulk",
      bulk_list=json.dumps([{"relative_url": document.getRelativeUrl(), "view": "view"}])
    )
    self.assertEquals(fake_request.RESPONSE.status, 200)
    self.assertEquals(fake_request.RESPONSE.getHeader('Content-Type'),
      "application/hal+json"
    )
    result_dict = json.loads(result)
    self.assertEqual(result_dict['_links']['self'], {"href": "http://example.org/bar"})

    self.assertEqual(len(result_dict['result_list']), 1)
    self.assertEqual(result_dict['result_list'][0]['_links']['self'], {"href": "http://example.org/bar"})
    self.assertEqual(result_dict['result_list'][0]['_links']['parent'],
                    {"href": "urn:jio:get:%s" % parent.getRelativeUrl(), "name": parent.getTitle()})

    self.assertEqual(result_dict['result_list'][0]['_links']['view'][0]['href'],
                     "%s/web_site_module/hateoas/ERP5Document_getHateoas?mode=traverse&relative_url=%s&view=view" % (
                       self.portal.absolute_url(),
                       urllib.quote_plus(document.getRelativeUrl())))
    self.assertEqual(result_dict['result_list'][0]['_links']['view'][0]['title'], "View")
    self.assertEqual(result_dict['result_list'][0]['_links']['view'][0]['name'], "view")

    self.assertEqual(result_dict['result_list'][0]['_links']['action_object_view'][0]['href'],
                     "%s/web_site_module/hateoas/ERP5Document_getHateoas?mode=traverse&relative_url=%s&view=view" % (
                       self.portal.absolute_url(),
                       urllib.quote_plus(document.getRelativeUrl())))
    self.assertEqual(result_dict['result_list'][0]['_links']['action_object_view'][0]['title'], "View")
    self.assertEqual(result_dict['result_list'][0]['_links']['action_object_view'][0]['name'], "view")

    self.assertEqual(result_dict['result_list'][0]['_links']['action_workflow'][0]['href'],
                     "%s/web_site_module/hateoas/ERP5Document_getHateoas?mode=traverse&relative_url=%s&view=custom_action_no_dialog" % (
                       self.portal.absolute_url(),
                       urllib.quote_plus(document.getRelativeUrl())))
    self.assertEqual(result_dict['result_list'][0]['_links']['action_workflow'][0]['title'], "Custom Action No Dialog")
    self.assertEqual(result_dict['result_list'][0]['_links']['action_workflow'][0]['name'], "custom_action_no_dialog")

    self.assertEqual(result_dict['result_list'][0]['_links']['portal']['href'], 'urn:jio:get:%s' % document.getPortalObject().getId())
    self.assertEqual(result_dict['result_list'][0]['_links']['portal']['name'], document.getPortalObject().getTitle())

    self.assertEqual(result_dict['result_list'][0]['_links']['site_root']['href'], 'urn:jio:get:web_site_module/hateoas')
    self.assertEqual(result_dict['result_list'][0]['_links']['site_root']['name'], self.portal.web_site_module.hateoas.getTitle())

    self.assertEqual(result_dict['result_list'][0]['_links']['action_object_new_content_action']['href'],
                     "%s/web_site_module/hateoas/ERP5Document_getHateoas?mode=traverse&relative_url=%s&view=create_a_document" % (
                       self.portal.absolute_url(),
                       urllib.quote_plus(document.getRelativeUrl())))
    self.assertEqual(result_dict['result_list'][0]['_links']['action_object_new_content_action']['title'], "Create a Document")
    self.assertEqual(result_dict['result_list'][0]['_links']['action_object_new_content_action']['name'], "create_a_document")

    self.assertEqual(result_dict['result_list'][0]['_links']['type']['href'], 'urn:jio:get:portal_types/%s' % document.getPortalType())
    self.assertEqual(result_dict['result_list'][0]['_links']['type']['name'], document.getPortalType())

    self.assertEqual(result_dict['result_list'][0]['title'].encode("UTF-8"), document.getTitle())
    self.assertEqual(result_dict['result_list'][0]['_debug'], "traverse")

    # Check embedded form rendering
    self.assertEqual(result_dict['result_list'][0]['_embedded']['_view']['form_id']['default'], 'Foo_view')
    self.assertEqual(result_dict['result_list'][0]['_embedded']['_view']['form_id']['editable'], 0)
    self.assertEqual(result_dict['result_list'][0]['_embedded']['_view']['form_id']['hidden'], 1)
    self.assertEqual(result_dict['result_list'][0]['_embedded']['_view']['form_id']['key'], 'form_id')
    self.assertEqual(result_dict['result_list'][0]['_embedded']['_view']['form_id']['required'], 1)
    self.assertEqual(result_dict['result_list'][0]['_embedded']['_view']['form_id']['type'], 'StringField')

    self.assertEqual(result_dict['result_list'][0]['_embedded']['_view']['my_id']['default'], document.getId())
    self.assertEqual(result_dict['result_list'][0]['_embedded']['_view']['my_id']['editable'], 1)
    self.assertEqual(result_dict['result_list'][0]['_embedded']['_view']['my_id']['hidden'], 0)
    self.assertEqual(result_dict['result_list'][0]['_embedded']['_view']['my_id']['key'], 'field_my_id')
    self.assertEqual(result_dict['result_list'][0]['_embedded']['_view']['my_id']['required'], 1)
    self.assertEqual(result_dict['result_list'][0]['_embedded']['_view']['my_id']['type'], 'StringField')
    self.assertEqual(result_dict['result_list'][0]['_embedded']['_view']['my_id']['title'], 'ID')

    self.assertEqual(result_dict['result_list'][0]['_embedded']['_view']['_links']['traversed_document']['href'], 'urn:jio:get:%s' % document.getRelativeUrl())
    self.assertEqual(result_dict['result_list'][0]['_embedded']['_view']['_links']['traversed_document']['name'], document.getRelativeUrl())
    self.assertEqual(result_dict['result_list'][0]['_embedded']['_view']['_links']['traversed_document']['title'], document.getTitle().decode("UTF-8"))

    self.assertEqual(result_dict['result_list'][0]['_embedded']['_view']['_links']['self']['href'], "%s/%s/Foo_view" % (
                                                                                    self.portal.absolute_url(),
                                                                                    document.getRelativeUrl()))

    self.assertEqual(result_dict['result_list'][0]['_embedded']['_view']['_links']['form_definition']['href'], 'urn:jio:get:portal_skins/erp5_ui_test/Foo_view')
    self.assertEqual(result_dict['result_list'][0]['_embedded']['_view']['_links']['form_definition']['name'], 'Foo_view')

    self.assertEqual(result_dict['result_list'][0]['_embedded']['_view']['_actions']['put']['href'], '%s/web_site_module/hateoas/%s/Base_edit' % (
                                                                                     self.portal.absolute_url(),
                                                                                     document.getRelativeUrl()))
    self.assertEqual(result_dict['result_list'][0]['_embedded']['_view']['_actions']['put']['method'], 'POST')
