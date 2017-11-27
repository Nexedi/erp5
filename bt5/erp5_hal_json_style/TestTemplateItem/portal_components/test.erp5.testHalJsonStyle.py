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
  """Change skin for following commands and attribute resolution.

  Caution: In case of more annotations, this one has to be at the bottom (last)!
  """
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
  """Create temporary script in portal_skins/custom.

  In case of unexpectedly interrupted test you need to clean that folder manually!

  Examples of usage:

    @simulate('Base_getRequestHeader', '*args, **kwargs', 'return "application/hal+json"')
  Will make ERP5Document_getHateoas believe that any request accepts given MIME response.

    @simulate('Base_getRequestUrl', '*args, **kwargs', 'return "http://example.org/bar"')
  TBD.
  """
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

def createIndexedDocument():
  """Create a Foo document inside Foo module and pass it as "document" argument into wrapped function."""
  def decorator(func):
    def wrapped(self, *args, **kwargs):
      kwargs.update(document=self._makeDocument())
      self.portal.portal_caches.clearAllCache()
      self.tic()
      return func(self, *args, **kwargs)
    return wrapped
  return decorator

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
                     "%s/web_site_module/hateoas/ERP5Document_getHateoas?mode=search{&query,select_list*,limit*,sort_on*,local_roles*}" % self.portal.absolute_url())
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
  def test_getHateoasDocument_portal_workflow(self):
    fake_request = do_fake_request("GET")
    result = self.portal.web_site_module.hateoas.ERP5Document_getHateoas(REQUEST=fake_request, mode="traverse", relative_url='portal_workflow')
    self.assertEquals(fake_request.RESPONSE.status, 200)
    self.assertEquals(fake_request.RESPONSE.getHeader('Content-Type'),
      "application/hal+json"
    )
    result_dict = json.loads(result)
    self.assertEqual(result_dict['_links']['self'], {"href": "http://example.org/bar"})

    self.assertEqual(result_dict['_links']['action_worklist']['href'],
                     "%s/web_site_module/hateoas/ERP5Document_getHateoas?mode=worklist" % self.portal.absolute_url())

  @simulate('Base_getRequestUrl', '*args, **kwargs',
      'return "http://example.org/bar"')
  @simulate('Base_getRequestHeader', '*args, **kwargs',
            'return "application/hal+json"')
  @changeSkin('Hal')
  def test_getHateoasDocument_default_view(self):
    document = self._makeDocument()
    document.Foo_view.listbox.ListBox_setPropertyList(
      field_title = 'Foo Lines',
      field_list_method = 'objectValues',
      field_portal_types = 'Foo Line | Foo Line',
      field_stat_method = 'portal_catalog',
      field_stat_columns = 'quantity | Foo_statQuantity',
      field_editable = 1,
      field_columns = 'id|ID\ntitle|Title\nquantity|Quantity\nstart_date|Date\ncatalog.uid|Uid',
      field_editable_columns = 'id|ID\ntitle|Title\nquantity|quantity\nstart_date|Date',
      field_search_columns = 'id|ID\ntitle|Title\nquantity|Quantity\nstart_date|Date',)

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

    self.assertEqual(result_dict['_links']['action_object_jump']['href'],
                     "urn:jio:allDocs?query=portal_type%%3A%%22Query%%22%%20AND%%20default_agent_uid%%3A%sL" %
                       document.getUid())
    self.assertEqual(result_dict['_links']['action_object_jump']['title'], "Queries")
    self.assertEqual(result_dict['_links']['action_object_jump']['name'], "jump_query")

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

    self.assertSameSet(result_dict['_embedded']['_view']['listbox']['default_params'].keys(), ['ignore_unknown_columns'])
    self.assertTrue(result_dict['_embedded']['_view']['listbox']['default_params']['ignore_unknown_columns'])
    self.assertEqual(result_dict['_embedded']['_view']['listbox']['type'], 'ListBox')
    self.assertEqual(result_dict['_embedded']['_view']['listbox']['key'], 'field_listbox')
    self.assertEqual(result_dict['_embedded']['_view']['listbox']['title'], 'Foo Lines')
    self.assertEqual(result_dict['_embedded']['_view']['listbox']['lines'], 3)
    self.assertEqual(result_dict['_embedded']['_view']['listbox']['editable'], 1)
    self.assertEqual(result_dict['_embedded']['_view']['listbox']['show_anchor'], 0)
    self.assertEqual(result_dict['_embedded']['_view']['listbox']['list_method'], 'objectValues')
    self.assertEqual(result_dict['_embedded']['_view']['listbox']['query'], 'urn:jio:allDocs?query=')
    self.assertEqual(result_dict['_embedded']['_view']['listbox']['portal_type'], [['Foo Line', 'Foo Line']])
    self.assertEqual(result_dict['_embedded']['_view']['listbox']['column_list'], [['id', 'ID'], ['title', 'Title'], ['quantity', 'Quantity'], ['start_date', 'Date'], ['catalog.uid', 'Uid']])
    self.assertEqual(result_dict['_embedded']['_view']['listbox']['search_column_list'], [['id', 'ID'], ['title', 'Title'], ['quantity', 'Quantity'], ['start_date', 'Date']])
    self.assertEqual(result_dict['_embedded']['_view']['listbox']['editable_column_list'], [['id', 'ID'], ['title', 'Title'], ['quantity', 'quantity'], ['start_date', 'Date']])
    self.assertEqual(result_dict['_embedded']['_view']['listbox']['sort_column_list'], [['id', 'ID'], ['title', 'Title'], ['quantity', 'Quantity'], ['start_date', 'Date']])
    self.assertEqual(result_dict['_embedded']['_view']['listbox']['list_method_template'],
                     '%s/web_site_module/hateoas/ERP5Document_getHateoas?mode=search&relative_url=foo_module%%2F%s&form_relative_url=portal_skins/erp5_ui_test/Foo_view/listbox&list_method=objectValues&default_param_json=eyJwb3J0YWxfdHlwZSI6IFsiRm9vIExpbmUiXSwgImlnbm9yZV91bmtub3duX2NvbHVtbnMiOiB0cnVlfQ=={&query,select_list*,limit*,sort_on*,local_roles*}' % (self.portal.absolute_url(), document.getId()))

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
  def test_getHateoasDocument_non_editable_default_view(self):
    document = self._makeDocument()
    # Drop editable permission
    document.manage_permission('Modify portal content', [], 0)
    document.Foo_view.listbox.ListBox_setPropertyList(
      field_title = 'Foo Lines',
      field_list_method = 'objectValues',
      field_portal_types = 'Foo Line | Foo Line',
      field_stat_method = 'portal_catalog',
      field_stat_columns = 'quantity | Foo_statQuantity',
      field_editable = 1,
      field_columns = 'id|ID\ntitle|Title\nquantity|Quantity\nstart_date|Date\ncatalog.uid|Uid',
      field_editable_columns = 'id|ID\ntitle|Title\nquantity|quantity\nstart_date|Date',
      field_search_columns = 'id|ID\ntitle|Title\nquantity|Quantity\nstart_date|Date',)

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

    self.assertFalse(result_dict['_embedded']['_view'].has_key('_actions'))


  @simulate('Base_getRequestUrl', '*args, **kwargs',
      'return "http://example.org/bar"')
  @simulate('Base_getRequestHeader', '*args, **kwargs',
            'return "application/hal+json"')
  @changeSkin('Hal')
  def test_getHateoasDocument_report_view(self):
    document = self._makeDocument()

    fake_request = do_fake_request("GET")
    result = self.portal.web_site_module.hateoas.ERP5Document_getHateoas(REQUEST=fake_request, mode="traverse", relative_url=document.getRelativeUrl(), view="history")
    self.assertEquals(fake_request.RESPONSE.status, 200)
    self.assertEquals(fake_request.RESPONSE.getHeader('Content-Type'),
      "application/hal+json"
    )
    result_dict = json.loads(result)

    # Check embedded form rendering
    self.assertEqual(result_dict['_embedded']['_view']['form_id']['default'], 'Base_viewHistory')
    self.assertEqual(result_dict['_embedded']['_view']['form_id']['editable'], 0)
    self.assertEqual(result_dict['_embedded']['_view']['form_id']['hidden'], 1)
    self.assertEqual(result_dict['_embedded']['_view']['form_id']['key'], 'form_id')
    self.assertEqual(result_dict['_embedded']['_view']['form_id']['required'], 1)
    self.assertEqual(result_dict['_embedded']['_view']['form_id']['type'], 'StringField')

    self.assertEqual(result_dict['_embedded']['_view']['your_zodb_history']['title'], 'View ZODB History')
    self.assertEqual(result_dict['_embedded']['_view']['your_zodb_history']['key'], 'field_your_zodb_history')
    self.assertEqual(result_dict['_embedded']['_view']['your_zodb_history']['type'], 'LinkField')

    # Check embedded report section rendering
    self.assertEqual(result_dict['_embedded']['_view']['report_section_list'][1]['form_id']['default'], 'Base_viewWorkflowHistory')
    self.assertEqual(result_dict['_embedded']['_view']['report_section_list'][1]['form_id']['editable'], 0)
    self.assertEqual(result_dict['_embedded']['_view']['report_section_list'][1]['form_id']['hidden'], 1)
    self.assertEqual(result_dict['_embedded']['_view']['report_section_list'][1]['form_id']['key'], 'form_id')
    self.assertEqual(result_dict['_embedded']['_view']['report_section_list'][1]['form_id']['required'], 1)
    self.assertEqual(result_dict['_embedded']['_view']['report_section_list'][1]['form_id']['type'], 'StringField')

    self.assertEqual(result_dict['_embedded']['_view']['report_section_list'][1]['_links']['traversed_document']['href'], 'urn:jio:get:%s' % document.getRelativeUrl())
    self.assertEqual(result_dict['_embedded']['_view']['report_section_list'][1]['_links']['traversed_document']['name'], document.getRelativeUrl())
    self.assertEqual(result_dict['_embedded']['_view']['report_section_list'][1]['_links']['traversed_document']['title'], document.getTitle().decode("UTF-8"))

    self.assertEqual(result_dict['_embedded']['_view']['report_section_list'][1]['_links']['form_definition']['href'], 'urn:jio:get:portal_skins/erp5_core/Base_viewWorkflowHistory')
    self.assertEqual(result_dict['_embedded']['_view']['report_section_list'][1]['_links']['form_definition']['name'], 'Base_viewWorkflowHistory')

    self.assertSameSet(result_dict['_embedded']['_view']['report_section_list'][1]['listbox']['default_params'].keys(), ['checked_permission', 'ignore_unknown_columns', 'workflow_id', 'workflow_title'])
    self.assertTrue(result_dict['_embedded']['_view']['report_section_list'][1]['listbox']['default_params']['ignore_unknown_columns'])
    self.assertEqual(result_dict['_embedded']['_view']['report_section_list'][1]['listbox']['default_params']['checked_permission'], 'View')
    self.assertEqual(result_dict['_embedded']['_view']['report_section_list'][1]['listbox']['default_params']['workflow_id'], 'foo_workflow')
    self.assertEqual(result_dict['_embedded']['_view']['report_section_list'][1]['listbox']['default_params']['workflow_title'], 'Foo Workflow')
    self.assertEqual(result_dict['_embedded']['_view']['report_section_list'][1]['listbox']['type'], 'ListBox')
    self.assertEqual(result_dict['_embedded']['_view']['report_section_list'][1]['listbox']['key'], 'x1_listbox')
    self.assertEqual(result_dict['_embedded']['_view']['report_section_list'][1]['listbox']['title'], 'Workflow History')
    self.assertEqual(result_dict['_embedded']['_view']['report_section_list'][1]['listbox']['lines'], 15)
    self.assertEqual(result_dict['_embedded']['_view']['report_section_list'][1]['listbox']['editable'], 1)
    self.assertEqual(result_dict['_embedded']['_view']['report_section_list'][1]['listbox']['show_anchor'], 0)
    self.assertEqual(result_dict['_embedded']['_view']['report_section_list'][1]['listbox']['list_method'], 'Base_getWorkflowHistoryItemList')
    self.assertEqual(result_dict['_embedded']['_view']['report_section_list'][1]['listbox']['query'], 'urn:jio:allDocs?query=')
    self.assertEqual(result_dict['_embedded']['_view']['report_section_list'][1]['listbox']['portal_type'], [])
    self.assertEqual(result_dict['_embedded']['_view']['report_section_list'][1]['listbox']['column_list'], [['action', 'Action'], ['state', 'State'], ['actor', 'Actor'], ['time', 'Time'], ['comment', 'Comment'], ['error_message', 'Error Message']])
    self.assertEqual(result_dict['_embedded']['_view']['report_section_list'][1]['listbox']['search_column_list'], [])
    self.assertEqual(result_dict['_embedded']['_view']['report_section_list'][1]['listbox']['editable_column_list'], [['time', 'Time'], ['comment', 'Comment'], ['error_message', 'Error Message']])
    self.assertEqual(result_dict['_embedded']['_view']['report_section_list'][1]['listbox']['sort_column_list'], [])
    self.assertEqual(result_dict['_embedded']['_view']['report_section_list'][1]['listbox']['list_method_template'],
                     '%s/web_site_module/hateoas/ERP5Document_getHateoas?mode=search&relative_url=foo_module%%2F%s&form_relative_url=portal_skins/erp5_core/Base_viewWorkflowHistory/listbox&list_method=Base_getWorkflowHistoryItemList&default_param_json=eyJ3b3JrZmxvd19pZCI6ICJmb29fd29ya2Zsb3ciLCAicG9ydGFsX3R5cGUiOiBbXSwgImNoZWNrZWRfcGVybWlzc2lvbiI6ICJWaWV3IiwgIndvcmtmbG93X3RpdGxlIjogIkZvbyBXb3JrZmxvdyIsICJpZ25vcmVfdW5rbm93bl9jb2x1bW5zIjogdHJ1ZX0={&query,select_list*,limit*,sort_on*,local_roles*}' % (self.portal.absolute_url(), document.getId()))


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
    self.assertEqual(result_dict['group_list'][0][1][0], ['my_id', {'meta_type': 'ProxyField'}])
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
    self.assertEqual(result_dict['_local_roles'], None)
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
    self.assertEqual(result_dict['_local_roles'], None)
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
    self.assertEqual(result_dict['_local_roles'], None)
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
    self.assertEqual(result_dict['_local_roles'], None)
    self.assertEqual(result_dict['_select_list'], [])

    self.assertEqual(len(result_dict['_embedded']['contents']), 0)

  @simulate('Base_getRequestUrl', '*args, **kwargs',
      'return "http://example.org/bar"')
  @simulate('Base_getRequestHeader', '*args, **kwargs',
            'return "application/hal+json"')
  @changeSkin('Hal')
  def test_getHateoas_local_roles_param(self):
    fake_request = do_fake_request("GET")
    result = self.portal.web_site_module.hateoas.ERP5Document_getHateoas(REQUEST=fake_request, mode="search", local_roles=["Assignor", "Assignee"])
    self.assertEquals(fake_request.RESPONSE.status, 200)
    self.assertEquals(fake_request.RESPONSE.getHeader('Content-Type'),
      "application/hal+json"
    )
    result_dict = json.loads(result)
    self.assertEqual(result_dict['_links']['self'], {"href": "http://example.org/bar"})

    self.assertEqual(result_dict['_debug'], "search")
    self.assertEqual(result_dict['_limit'], 10)
    self.assertEqual(result_dict['_query'], None)
    self.assertEqual(result_dict['_local_roles'], ["Assignor", "Assignee"])
    self.assertEqual(result_dict['_select_list'], [])

    self.assertEqual(len(result_dict['_embedded']['contents']), 0)

  @simulate('Base_getRequestUrl', '*args, **kwargs',
      'return "http://example.org/bar"')
  @simulate('Base_getRequestHeader', '*args, **kwargs',
            'return "application/hal+json"')
  @changeSkin('Hal')
  def test_getHateoas_default_param_json_param(self):
    fake_request = do_fake_request("GET")

    self.assertRaisesRegexp(
      TypeError,
      # "Unknown columns.*'\\xc3\\xaa'.",
      "Unknown columns.*\\\\xc3\\\\xaa.*",
      self.portal.web_site_module.hateoas.ERP5Document_getHateoas,
      REQUEST=fake_request,
      mode="search",
      default_param_json='eyJcdTAwZWEiOiAiXHUwMGU4In0=')

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

class TestERP5Document_getHateoas_mode_worklist(ERP5HALJSONStyleSkinsMixin):

  @simulate('Base_getRequestHeader', '*args, **kwargs',
            'return "application/hal+json"')
  @changeSkin('Hal')
  def test_getHateoasWorklist_bad_method(self):
    fake_request = do_fake_request("POST")
    result = self.portal.web_site_module.hateoas.ERP5Document_getHateoas(REQUEST=fake_request, mode="worklist")
    self.assertEquals(fake_request.RESPONSE.status, 405)
    self.assertEquals(result, "")


  @simulate('Base_getRequestUrl', '*args, **kwargs',
      'return "http://example.org/bar"')
  @simulate('Base_getRequestHeader', '*args, **kwargs',
            'return "application/hal+json"')
  @createIndexedDocument()
  @changeSkin('Hal')
  def test_getHateoasWorklist_default_view(self, document):
    # self._makeDocument()
    fake_request = do_fake_request("GET")
    result = self.portal.web_site_module.hateoas.ERP5Document_getHateoas(
      REQUEST=fake_request,
      mode="worklist"
    )
    self.assertEquals(fake_request.RESPONSE.status, 200)
    self.assertEquals(fake_request.RESPONSE.getHeader('Content-Type'),
      "application/hal+json"
    )
    result_dict = json.loads(result)
    self.assertEqual(result_dict['_links']['self'], {"href": "http://example.org/bar"})

    work_list = [x for x in result_dict['worklist'] if x['name'].startswith('Draft To Validate')]
    self.assertEqual(len(work_list), 1)
    self.assertTrue(work_list[0]['count'] > 0)
    self.assertEqual(work_list[0]['name'], 'Draft To Validate')
    self.assertFalse('module' in work_list[0])
    self.assertEqual(work_list[0]['href'], 'urn:jio:allDocs?query=portal_type%3A%28%22Bar%22%20OR%20%22Foo%22%29%20AND%20simulation_state%3A%22draft%22')

    self.assertEqual(result_dict['_debug'], "worklist")

class TestERP5Document_getHateoas_translation(ERP5HALJSONStyleSkinsMixin):
  code_string = "\
from Products.CMFCore.utils import getToolByName\n\
translation_service = getToolByName(context, 'Localizer', None)\n\
if translation_service is not None :\n\
  try:\n\
    if not encoding:\n\
      return translation_service.translate(catalog, msg, lang=lang, **kw)\n\
    msg = translation_service.translate(catalog, msg, lang=lang, **kw)\n\
    if same_type(msg, u''):\n\
      msg = msg.encode(encoding)\n\
    return msg\n\
  except AttributeError:\n\
    pass\n\
return msg"

  @simulate('Base_getRequestUrl', '*args, **kwargs',
      'return "http://example.org/bar"')
  @simulate('Base_getRequestHeader', '*args, **kwargs',
            'return "application/hal+json"')
  @simulate('Base_translateString', 'msg, catalog="ui", encoding="utf8", lang="wo", **kw',
  code_string)

  @changeSkin('Hal')
  def test_getHateoasBulk_default_view_translation(self):
    self.portal.Base_createUITestLanguages()
    param_dict = [
      { 'message': 'Title', 'translation': 'biaoti', 'language': 'wo'},
      { 'message': 'Draft To Validate', 'translation': 'daiyanzhen', 'language': 'wo'},
      { 'message': 'Foo', 'translation': 'Foo_zhongwen', 'language': 'wo'}]
    for tmp in param_dict:
      self.portal.Base_addUITestTranslation(message = tmp['message'], translation = tmp['translation'], language = tmp['language'])
    document = self._makeDocument()
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
    self.assertEqual(result_dict['result_list'][0]['_embedded']['_view']['my_title']['title'], 'biaoti')
    self.assertEqual(result_dict['result_list'][0]['_links']['type']['name'], 'Foo_zhongwen')
    self.assertEqual(result_dict['result_list'][0]['_embedded']['_view']['listbox']['column_list'][1][1], 'biaoti')

  @simulate('Base_getRequestUrl', '*args, **kwargs',
      'return "http://example.org/bar"')
  @simulate('Base_getRequestHeader', '*args, **kwargs',
            'return "application/hal+json"')
  @simulate('Base_translateString', 'msg, catalog="ui", encoding="utf8", lang="wo", **kw',
  code_string)

  @changeSkin('Hal')
  def test_getHateoasDocument_result_translation(self):
    document = self._makeDocument()
    fake_request = do_fake_request("GET")
    result = document.ERP5Document_getHateoas(REQUEST=fake_request)
    self.assertEquals(fake_request.RESPONSE.status, 200)
    self.assertEquals(fake_request.RESPONSE.getHeader('Content-Type'),
      "application/hal+json"
    )
    result_dict = json.loads(result)

    self.assertEqual(result_dict['_links']['type']['href'], 'urn:jio:get:portal_types/%s' % document.getPortalType())
    self.assertEqual(result_dict['_links']['type']['name'], 'Foo_zhongwen')

    self.assertEqual(result_dict['title'].encode("UTF-8"), document.getTitle())
    self.assertEqual(result_dict['_debug'], "root")

  @simulate('Base_getRequestUrl', '*args, **kwargs',
      'return "http://example.org/bar"')
  @simulate('Base_getRequestHeader', '*args, **kwargs',
            'return "application/hal+json"')
  @simulate('Base_translateString', 'msg, catalog="ui", encoding="utf8", lang="wo", **kw',
  code_string)
  @changeSkin('Hal')
  def test_getHateoasWorklist_default_view_translation(self):
    # self._makeDocument()
    fake_request = do_fake_request("GET")
    result = self.portal.web_site_module.hateoas.ERP5Document_getHateoas(
      REQUEST=fake_request,
      mode="worklist"
    )
    self.assertEquals(fake_request.RESPONSE.status, 200)
    self.assertEquals(fake_request.RESPONSE.getHeader('Content-Type'),
      "application/hal+json"
    )
    result_dict = json.loads(result)
    self.assertEqual(result_dict['_links']['self'], {"href": "http://example.org/bar"})
    work_list = [x for x in result_dict['worklist'] if x['name'].startswith('daiyanzhen')]
    self.assertEqual(len(work_list), 1)
    self.assertEqual(work_list[0]['name'], 'daiyanzhen')
    self.assertTrue(work_list[0]['count'] > 0)
    self.assertFalse('module' in work_list[0])
    self.assertEqual(work_list[0]['href'], 'urn:jio:allDocs?query=portal_type%3A%28%22Bar%22%20OR%20%22Foo%22%29%20AND%20simulation_state%3A%22draft%22')

    self.assertEqual(result_dict['_debug'], "worklist")

  @simulate('Base_getRequestUrl', '*args, **kwargs',
      'return "http://example.org/bar"')
  @simulate('Base_getRequestHeader', '*args, **kwargs',
            'return "application/hal+json"')
  @simulate('Base_translateString', 'msg, catalog="ui", encoding="utf8", lang="wo", **kw',
  code_string)
  @changeSkin('Hal')
  def test_getHateoasForm_no_view(self):
    fake_request = do_fake_request("GET")
    result = self.portal.web_site_module.hateoas.ERP5Document_getHateoas(REQUEST=fake_request, mode="traverse", relative_url="portal_skins/erp5_ui_test/Foo_view")
    self.assertEquals(fake_request.RESPONSE.status, 200)
    self.assertEquals(fake_request.RESPONSE.getHeader('Content-Type'),
      "application/hal+json"
    )
    result_dict = json.loads(result)
    self.assertEqual(result_dict['title'], 'Foo_zhongwen')


class TestERP5Action_getHateoas(ERP5HALJSONStyleSkinsMixin):

  @simulate('Base_getRequestHeader', '*args, **kwargs',
            'return "application/hal+json"')
  @createIndexedDocument()
  @changeSkin('Hal')
  def test_getHateoasDialog_dialog_failure(self, document):
    """Test an dialog on Foo object with empty required for a failure.
    
    Expected behaviour is response Http 400 with field errors.
    """
    fake_request = do_fake_request("POST")
    # user form fields
    # no need to set meta-fields because we pass them directly to script)
    fake_request.set('field_your_workflow_action', 'custom_dialog_required_action')
    fake_request.set('field_your_comment', 'My comment')
    fake_request.set('field_your_custom_workflow_variable',  '')  # empty required field!

    # call the standard dialog submit script - should return plain string bytes
    method_path = document.Base_callDialogMethod.aq_self._filepath
    self.assertIn("erp5_hal_json_style", method_path,
                  "Script from \"erp5_hal_json_style\" must be selected - not \"{!s}\"".format(method_path))
    response = document.Base_callDialogMethod(
      REQUEST=fake_request,
      dialog_method='Foo_doNothing',  # 'Workflow_statusModify' would lead us by a different path in the code
      dialog_id='Foo_viewCustomWorkflowRequiredActionDialog',
    )
    self.assertEqual(fake_request.RESPONSE.status, 400)

    response = json.loads(response)

    self.assertIn('your_custom_workflow_variable', response, "Invalid field '{}' must be in the response {!s}".format(
      'your_custom_workflow_variable', response))
    self.assertIn('error_text', response['your_custom_workflow_variable'], "Invalid field must contain error message")
    self.assertGreater(len(response['your_custom_workflow_variable']['error_text']), 0, "Error message must not be empty")
    