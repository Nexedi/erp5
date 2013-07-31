##############################################################################
#
# Copyright (c) 2002-2013 Nexedi SA and Contributors. All Rights Reserved.
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsibility of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# guarantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
##############################################################################

from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from Products.ERP5Type.Log import log

import json
import re
import random

def UTF8DeepJsonEncoder(obj):
    # string -> unicode -> str
    if isinstance(obj, unicode):
        return obj.encode("UTF-8")
    # array -> list
    if isinstance(obj, list):
        for i in xrange(len(obj)):
            obj[i] = UTF8DeepJsonEncoder(obj[i])
        return obj
    # object -> dict
    if isinstance(obj, dict):
        for k, v in obj.items():
            v = UTF8DeepJsonEncoder(v)
            del obj[k]
            obj[UTF8DeepJsonEncoder(k)] = v
        return obj
    # number (int) -> int, long
    # true -> True
    # false -> False
    # null -> None
    return obj

def json_loads(string):
  return UTF8DeepJsonEncoder(json.loads(string))

class TestJIO(ERP5TypeTestCase):
  """
  A JIO Test Class
  """

  def getTitle(self):
    return "JIO Test"

  def getBusinessTemplateList(self):
    """
    Tuple of Business Templates we need to install
    """
    return (
      'erp5_base',
      'erp5_core_proxy_field_legacy',
      'erp5_dms',
      'erp5_jio',
    )

  DOCUMENT_TEST_TITLE1 = "Tests Tests Tests Tests Tests Tests Tests Tests"
  DOCUMENT_TEST_TITLE2 = "Tests Tests Tests Tests Tests Tests Tests"
  WRONG_MODULE_NAME = "bah_blue_module"

  def afterSetUp(self):
    """
    This is ran before anything, used to set the environment
    """
    pass

  def findFreeWebPageId(self):
    web_page_module = self.getPortalObject()["web_page_module"]
    while True:
      i = str(random.randint(0, 99999999))
      if i not in web_page_module:
        return i

  def assertStatusCode(self, result, expected):
    """Check the error status code of an erp5 jio script result

    Arguments:
    - `result`: The jio script result, can be a parsable json string or a dict
    - `expected`: The expected status code
    """
    if isinstance(result, str): result = json_loads(result)

    message = "Expected error status code: " + str(expected)
    def assertWrongStatusCode():
      return self.assertEqual(result, expected, message)

    try: err = result["err"]
    except KeyError: return assertWrongStatusCode()
    if err is None: return assertWrongStatusCode()

    try: status = err["status"]
    except KeyError: return assertWrongStatusCode()

    return self.assertEqual(status, expected, message)

  def assertResponse(self, result, expected):
    """Check the response of an erp5 jio script result

    Arguments:
    - `result`: The jio script result, can be a parsable json string or a dict
    - `expected`: The expected response json dict
    """
    if isinstance(result, str): result = json_loads(result)

    message = "Expected response: " + json.dumps(expected)
    def assertWrongResponse():
      return self.assertEqual(json.dumps(result), message)

    try: response = result["response"]
    except KeyError: return assertWrongResponse()
    if response is None: return assertWrongResponse()
    return self.assertEqual(response, expected)

  # def test_01_sampleTest(self):
  #   """
  #   A Sample Test

  #   For the method to be called during the test,
  #   its name must start with 'test'.
  #   The '_01_' part of the name is not mandatory,
  #   it just allows you to define in which order the tests are to be launched.
  #   Tests methods (self.assert... and self.failIf...)
  #   are defined in /usr/lib/python/unittest.py.
  #   """
  #   # portal = self.getPortalObject()
  #   # portal.JIO_getClass(foo='bar')
  #   self.assertEqual(1, 1)

  def test_01_jioGenericPost(self):
    self.login()
    portal = self.getPortalObject()
    web_page_id = self.findFreeWebPageId()

    # post document without id nor type
    portal.REQUEST.form.update({"doc": json.dumps({
      # "type": "Web Page",
      "title": self.DOCUMENT_TEST_TITLE1,
      "category": ["a/b/c", "d/e/f"],
    })})

    self.assertStatusCode(portal.JIO_post(), 409)

    # post document without id, with type
    portal.REQUEST.form.update({"doc": json.dumps({
      "type": "Web Page",
      "title": self.DOCUMENT_TEST_TITLE1,
      "category": ["a/b/c", "d/e/f"],
    })})

    result = json_loads(portal.JIO_post())
    response = result["response"]
    self.assertEqual(response["id"].split("/")[:-1],
                     ["", "web_page_module"])
    self.assertResponse(result, {"ok": True, "id": response["id"]})

    # check new document object
    split_id = response["id"].split("/")
    _, module_id, document_id = response["id"].split("/")
    document = portal[split_id[1]][split_id[2]]
    self.assertEqual(document.getPortalType(), "Web Page")
    self.assertEqual(document.getTitle(),self.DOCUMENT_TEST_TITLE1)
    self.assertEqual(document.getCategoriesList(), ["a/b/c", "d/e/f"])

    # post with wrong id, with type
    portal.REQUEST.form.update({"doc": json.dumps({
      "_id": "/" + self.WRONG_MODULE_NAME + "/" + web_page_id,
      "type": "Web Page",
      "title": self.DOCUMENT_TEST_TITLE1,
      "category": ["a/b/c", "d/e/f"],
    })})

    self.assertStatusCode(portal.JIO_post(), 409)

    # post document with id, with type
    portal.REQUEST.form.update({"doc": json.dumps({
      "_id": "/web_page_module/" + web_page_id,
      "type": "Web Page",
      "title": self.DOCUMENT_TEST_TITLE1,
      "category": ["a/b/c", "d/e/f"],
    })})

    self.assertResponse(portal.JIO_post(), {
        "ok": True, "id": "/web_page_module/" + web_page_id
    })

    # check new document object
    document = portal["web_page_module"][web_page_id]
    self.assertEqual(document.getPortalType(), "Web Page")
    self.assertEqual(document.getTitle(),self.DOCUMENT_TEST_TITLE1)
    self.assertEqual(document.getCategoriesList(), ["a/b/c", "d/e/f"])

    # post document with same id, with same type
    self.assertStatusCode(portal.JIO_post(), 409)

  def test_02_jioGenericPutAttachment(self):
    self.login()
    portal = self.getPortalObject()
    web_page_id = self.findFreeWebPageId()

    # post a document
    portal.REQUEST.form.update({"doc": json.dumps({
      "_id": "/web_page_module/" + web_page_id,
      "type": "Web Page",
      "title": self.DOCUMENT_TEST_TITLE1
    })})

    portal.JIO_post()

    # put a new attachment with random document id
    portal.REQUEST.form.update({"doc": json.dumps({
      "_id": "/" + self.WRONG_MODULE_NAME + "/" + web_page_id,
      "_attachment": "aeousaoechu",
      "_data": "<p>pouet</p>",
      "_mimetype": "text/html"
    })})

    self.assertStatusCode(portal.JIO_putAttachment(), 409)

    # put a new attachment with random id
    portal.REQUEST.form.update({"doc": json.dumps({
      "_id": "/web_page_module/" + web_page_id,
      "_attachment": "aeousaoechu",
      "_data": "<p>pouet</p>",
      "_mimetype": "text/html"
    })})

    self.assertStatusCode(portal.JIO_putAttachment(), 409)

    # put a new attachment with correct id
    portal.REQUEST.form.update({"doc": json.dumps({
      "_id": "/web_page_module/" + web_page_id,
      "_attachment": "body",
      "_data": "<p>pouet</p>",
      "_mimetype": "text/html"
    })})

    self.assertResponse(portal.JIO_putAttachment(), {
      "ok": True,
      "id": "/web_page_module/" + web_page_id,
      "attachment": "body"
    })

    # check new document object
    document = portal["web_page_module"][web_page_id]
    self.assertEqual(document.getData(), "<p>pouet</p>")

    # put a new attachment with 'body' as id
    portal.REQUEST.form.update({"doc": json.dumps({
      "_id": "/web_page_module/" + web_page_id,
      "_attachment": "body",
      "_data": "<p>yeah</p>",
      "_mimetype": "text/html"
    })})

    self.assertResponse(portal.JIO_putAttachment(), {
      "ok": True,
      "id": "/web_page_module/" + web_page_id,
      "attachment": "body"
    })

    # check new document object
    document = portal["web_page_module"][web_page_id]
    self.assertEqual(document.getData(), "<p>yeah</p>")

  def test_03_jioGenericGet(self):
    self.login()
    portal = self.getPortalObject()
    web_page_id = self.findFreeWebPageId()

    # get an wrong document
    portal.REQUEST.form.update({"doc": json.dumps({
      "_id": "/" + self.WRONG_MODULE_NAME + "/" + web_page_id,
    })})

    self.assertStatusCode(portal.JIO_get(), 404) # TODO should be 409

    # get an inexistent document
    portal.REQUEST.form.update({"doc": json.dumps({
      "_id": "/web_page_module/" + web_page_id,
    })})

    self.assertStatusCode(portal.JIO_get(), 404)

    # post a document
    portal.REQUEST.form.update({"doc": json.dumps({
      "_id": "/web_page_module/" + web_page_id,
      "type": "Web Page",
      "title": self.DOCUMENT_TEST_TITLE1,
      "category": ["a/b/c", "d/e/f"],
    })})

    portal.JIO_post()

    # get the document
    portal.REQUEST.form.update({"doc": json.dumps({
      "_id": "/web_page_module/" + web_page_id,
    })})

    result = json_loads(portal.JIO_get())
    if result.get("response") is not None:
      response = result["response"]
      # date, created and modified must exist
      del response["date"]
      del response["created"]
      del response["modified"]

    self.assertResponse(result, {
      "_id": "/web_page_module/" + web_page_id,
      "type": "Web Page",
      "title": self.DOCUMENT_TEST_TITLE1,
      "category": ["a/b/c", "d/e/f"],
      "format": "text/html"
    })

    # put an attachment
    portal.REQUEST.form.update({"doc": json.dumps({
      "_id": "/web_page_module/" + web_page_id,
      "_attachment": "body",
      "_data": "<p>yeah</p>",
      "_mimetype": "text/html"
    })})

    portal.JIO_putAttachment()

    # get the document
    portal.REQUEST.form.update({"doc": json.dumps({
      "_id": "/web_page_module/" + web_page_id,
    })})

    result = json_loads(portal.JIO_get())
    if result.get("response") is not None:
      response = result["response"]
      # date, created and modified must exist
      del response["date"]
      del response["created"]
      del response["modified"]

    self.assertResponse(result, {
      "_id": "/web_page_module/" + web_page_id,
      "type": "Web Page",
      "title": self.DOCUMENT_TEST_TITLE1,
      "category": ["a/b/c", "d/e/f"],
      "format": "text/html",
      "_attachments": {
        "body": {
          "length": 11,
          # "digest": "md5-xxx", # TODO
          "content_type": "text/html"
        }
      }
    })

  def test_04_jioGenericGetAttachment(self):
    self.login()
    portal = self.getPortalObject()
    web_page_id = self.findFreeWebPageId()

    # get an attachment from an inexistent document
    portal.REQUEST.form.update({"doc": json.dumps({
      "_id": "/" + self.WRONG_MODULE_NAME + "/" + web_page_id,
      "_attachment": "body"
    })})

    self.assertStatusCode(portal.JIO_getAttachment(), 404) # TODO should be 409

    # get an attachment from an inexistent document
    portal.REQUEST.form.update({"doc": json.dumps({
      "_id": "/web_page_module/" + web_page_id,
      "_attachment": "body"
    })})

    self.assertStatusCode(portal.JIO_getAttachment(), 404)

    # post a document
    portal.REQUEST.form.update({"doc": json.dumps({
      "_id": "/web_page_module/" + web_page_id,
      "type": "Web Page",
      "title": self.DOCUMENT_TEST_TITLE1,
      "category": ["a/b/c", "d/e/f"],
    })})

    portal.JIO_post()

    # get an inexistent attachment from a document
    portal.REQUEST.form.update({"doc": json.dumps({
      "_id": "/web_page_module/" + web_page_id,
      "_attachment": "aoercuha"
    })})

    self.assertStatusCode(portal.JIO_getAttachment(), 404) # TODO should be 409

    # get an inexistent attachment from a document
    portal.REQUEST.form.update({"doc": json.dumps({
      "_id": "/web_page_module/" + web_page_id,
      "_attachment": "body"
    })})

    self.assertStatusCode(portal.JIO_getAttachment(), 404)

    # put an attachment
    portal.REQUEST.form.update({"doc": json.dumps({
      "_id": "/web_page_module/" + web_page_id,
      "_attachment": "body",
      "_data": "<p>yeah</p>",
      "_mimetype": "text/html"
    })})

    portal.JIO_putAttachment()

    # get an attachment with 'body' as id
    portal.REQUEST.form.update({"doc": json.dumps({
      "_id": "/web_page_module/" + web_page_id,
      "_attachment": "body"
    })})

    self.assertResponse(portal.JIO_getAttachment(), "<p>yeah</p>")

  def test_05_jioGenericPut(self):
    self.login()
    portal = self.getPortalObject()
    web_page_id = self.findFreeWebPageId()

    # put without id
    portal.REQUEST.form.update({"doc": json.dumps({
      "type": "Web Page",
      "title": self.DOCUMENT_TEST_TITLE1,
      "category": ["a/b/c", "d/e/f"],
    })})

    self.assertStatusCode(portal.JIO_put(), 409)

    # put with wrong id
    portal.REQUEST.form.update({"doc": json.dumps({
      "_id": "/" + self.WRONG_MODULE_NAME + "/" + web_page_id,
      "type": "Web Page",
      "title": self.DOCUMENT_TEST_TITLE1,
      "category": ["a/b/c", "d/e/f"],
    })})

    self.assertStatusCode(portal.JIO_put(), 409)

    # put with correct id
    portal.REQUEST.form.update({"doc": json.dumps({
      "_id": "/web_page_module/" + web_page_id,
      "type": "Web Page",
      "title": self.DOCUMENT_TEST_TITLE1,
      "category": ["a/b/c", "d/e/f"],
    })})

    self.assertResponse(portal.JIO_put(), {
        "ok": True, "id": "/web_page_module/" + web_page_id
    })

    # check new document object
    document = portal["web_page_module"][web_page_id]
    self.assertEqual(document.getPortalType(), "Web Page")
    self.assertEqual(document.getTitle(), self.DOCUMENT_TEST_TITLE1)
    self.assertEqual(document.getCategoriesList(), ["a/b/c", "d/e/f"])

    # put with same id, different title
    portal.REQUEST.form.update({"doc": json.dumps({
      "_id": "/web_page_module/" + web_page_id,
      "type": "Web Page",
      "title": self.DOCUMENT_TEST_TITLE2,
      "category": ["a/b/c", "d/e/f"],
    })})

    self.assertResponse(portal.JIO_put(), {
        "ok": True, "id": "/web_page_module/" + web_page_id
    })

    # check new document object
    document = portal["web_page_module"][web_page_id]
    self.assertEqual(document.getPortalType(), "Web Page")
    self.assertEqual(document.getTitle(), self.DOCUMENT_TEST_TITLE2)
    self.assertEqual(document.getCategoriesList(), ["a/b/c", "d/e/f"])

  def test_06_jioGenericRemoveAttachment(self):
    self.login()
    portal = self.getPortalObject()
    web_page_id = self.findFreeWebPageId()

    # remove attachment from bad document
    portal.REQUEST.form.update({"doc": json.dumps({
      "_id": "/" + self.WRONG_MODULE_NAME + "/" + web_page_id,
      "_attachment": "body"
    })})

    self.assertStatusCode(portal.JIO_removeAttachment(), 404) # TODO should be 409

    # remove attachment from inexistent document
    portal.REQUEST.form.update({"doc": json.dumps({
      "_id": "/web_page_module/" + web_page_id,
      "_attachment": "body"
    })})

    self.assertStatusCode(portal.JIO_removeAttachment(), 404)

    # put a document
    portal.REQUEST.form.update({"doc": json.dumps({
      "_id": "/web_page_module/" + web_page_id,
      "type": "Web Page",
      "title": self.DOCUMENT_TEST_TITLE2,
      "category": ["a/b/c", "d/e/f"],
    })})

    portal.JIO_put()

    # remove bad attachment from document
    portal.REQUEST.form.update({"doc": json.dumps({
      "_id": "/web_page_module/" + web_page_id,
      "_attachment": "aoeucrh"
    })})

    self.assertStatusCode(portal.JIO_removeAttachment(), 409)

    # remove inexistent attachment from document
    portal.REQUEST.form.update({"doc": json.dumps({
      "_id": "/web_page_module/" + web_page_id,
      "_attachment": "body"
    })})

    self.assertStatusCode(portal.JIO_removeAttachment(), 404)

    # put an attachment
    portal.REQUEST.form.update({"doc": json.dumps({
      "_id": "/web_page_module/" + web_page_id,
      "_attachment": "body",
      "_data": "<p>yeah</p>",
      "_mimetype": "text/html"
    })})

    portal.JIO_putAttachment()

    # remove attachment
    portal.REQUEST.form.update({"doc": json.dumps({
      "_id": "/web_page_module/" + web_page_id,
      "_attachment": "body"
    })})

    self.assertResponse(portal.JIO_removeAttachment(), {
      "ok": True, "id": "/web_page_module/" + web_page_id,
        "attachment": "body"
    })

    # check document object
    document = portal["web_page_module"][web_page_id]
    self.assertEqual(document.getData(), None)


  def test_07_jioGenericRemove(self):
    self.login()
    portal = self.getPortalObject()
    web_page_id = self.findFreeWebPageId()

    # remove document with bad id
    portal.REQUEST.form.update({"doc": json.dumps({
      "_id": "/" + self.WRONG_MODULE_NAME + "/" + web_page_id
    })})

    self.assertStatusCode(portal.JIO_remove(), 404) # TODO should be 409

    # remove inexistent document
    portal.REQUEST.form.update({"doc": json.dumps({
      "_id": "/web_page_module/" + web_page_id
    })})

    self.assertStatusCode(portal.JIO_remove(), 404)

    # put a document
    portal.REQUEST.form.update({"doc": json.dumps({
      "_id": "/web_page_module/" + web_page_id,
      "type": "Web Page",
      "title": self.DOCUMENT_TEST_TITLE1,
      "category": ["a/b/c", "d/e/f"],
    })})

    portal.JIO_put()

    # remove document
    portal.REQUEST.form.update({"doc": json.dumps({
      "_id": "/web_page_module/" + web_page_id
    })})

    self.assertResponse(portal.JIO_remove(), {
        "ok": True, "id": "/web_page_module/" + web_page_id
    })

    # remove document
    portal.REQUEST.form.update({"doc": json.dumps({
      "_id": "/web_page_module/" + web_page_id
    })})

    self.assertStatusCode(portal.JIO_remove(), 404)


  def test_08_jioGenericAllDocs(self):
    self.login()
    portal = self.getPortalObject()
    web_page_id = self.findFreeWebPageId()
    title = "My very specific title from the JIO allDocs unit test"

    # put and commit a document
    portal.REQUEST.form.update({"doc": json.dumps({
      "_id": "/web_page_module/" + web_page_id,
      "type": "Web Page",
      "title": title,
      "category": ["a/b/c", "d/e/f"],
    })})


    portal.JIO_post()
    self.commit()
    self.tic()

    posted_document_found = False

    # get allDocs, then filter to get only web pages and sort
    portal.REQUEST.form.update({"doc": {}})

    expected = {}
    expected["rows"] = [{
        "id": "/web_page_module/" + document.getId(),
        "key": "/web_page_module/" + document.getId(),
        "value": {}
    } for document in portal.portal_catalog(portal_type="Web Page")]
    expected["total_rows"] = len(expected["rows"])
    expected["rows"].sort(key=lambda e: e["id"])

    result = json_loads(portal.JIO_allDocs())
    if result.get("response") is not None:
      response = result["response"]
      # filter to get only web pages
      i = 0
      while i < response["total_rows"]:
        if response["rows"][i]["id"].startswith("/web_page_module/"):
          if not posted_document_found and \
             response["rows"][i]["id"] == "/web_page_module/" + web_page_id:
            posted_document_found = True
          i += 1
        else:
          del response["rows"][i]
          response["total_rows"] -= 1
      # sort
      response["rows"].sort(key=lambda e: e["id"])

    self.assertEqual(posted_document_found, True,
                     "Just posted document not found in the allDocs response")
    self.assertResponse(result, expected)

    # get allDocs with a filter to get only web pages and sort
    portal.REQUEST.form.update({"option": json.dumps({
      "query": {
        "type": "simple",
        "operator": "=",
        "key": "type",
        "value": "Web Page"
      },
      "sort_on": [["created", "ascending"]]
    })})

    expected["rows"] = [{
        "id": "/web_page_module/" + document.getId(),
        "key": "/web_page_module/" + document.getId(),
        "value": {}
    } for document in portal.portal_catalog(
        portal_type="Web Page",
        sort_on=[('creation_date', 'ascending')]
    )]
    expected["total_rows"] = len(expected["rows"])

    self.assertResponse(portal.JIO_allDocs(), expected)

    # # get specific documents with a query
    portal.REQUEST.form.update({"option": json.dumps({
      "query": {
        "type": "simple",
        "operator": "=",
        "key": "title",
        "value": title
      }
    })})

    expected["rows"] = [{
        "id": "/web_page_module/" + document.getId(),
        "key": "/web_page_module/" + document.getId(),
        "value": {}
    } for document in portal.portal_catalog(
        title=title
    )]
    expected["total_rows"] = len(expected["rows"])

    self.assertResponse(portal.JIO_allDocs(), expected)

    # remove posted document
    portal.REQUEST.form.update({"doc": json.dumps({
      "_id": "/web_page_module/" + web_page_id
    })})
    portal.JIO_remove()
    self.commit()
    self.tic()
