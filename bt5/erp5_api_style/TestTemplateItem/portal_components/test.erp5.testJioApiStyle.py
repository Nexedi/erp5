##############################################################################
#
# Copyright (c) 2002-2021 Nexedi SA and Contributors. All Rights Reserved.
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

from DateTime import DateTime

import json

from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from Products.ERP5Type.tests.utils import createZODBPythonScript
import six


class TestjIOApiStyle(ERP5TypeTestCase):
  """
  Test jIO Api Style usage
  """

  def afterSetUp(self):
    """
    This is ran before anything, used to set the environment
    """
    self.login()
    self.base_id_template = "test_jio_api_style_live_test_data"
    self.cleanUpTestData()
    self.test_start_time = DateTime()
    self.dummy_web_site_id = "test_api"
    self.current_id = self.portal.portal_ids.generateNewId(
      id_group=repr(('reference', "test_jio_api_style")),
      default=1
    )
    self.id_template = self.base_id_template + "_%s" % self.current_id
    # Should be used as base for action_types and actions for garbage collect
    # Check Web Site and API Status
    if not self.dummy_web_site_id in self.portal.web_site_module:
      self.portal.web_site_module.newContent(
        portal_type="Web Site",
        title="Test API Web Site",
        id=self.dummy_web_site_id,
      )
    self.web_site = self.portal.web_site_module[self.dummy_web_site_id]
    if not "api" in self.web_site:
      self.web_site.newContent(
        portal_type="jIO Web Section",
        id="api",
        title="api",
        layout_configuration_form_id="WebSection_viewjIOStyleAPIPreference",
        custom_render_method_id="jIOWebSection_getAPIJSONHyperSchema",
        skin_selection_name='View',
      )
    self.api_web_section = self.web_site['api']
    self.action_type_dict = {
      "put": "object_json_api_put",
      "post": "object_json_api_post",
      "alldocs": "object_json_api_all_docs",
      "get": "object_json_api_get",
    }
    for key, action_type in six.iteritems(self.action_type_dict):
      self.updateCreateActionType(action_type)
      self.api_web_section.setProperty(
        "configuration_%s_action_type" % key,
        action_type
      )
    self.tic()

  def cleanUpTestData(self):
    self.tic()
    result_list = self.portal.portal_catalog(
      relative_url="%%/%s%%" % self.base_id_template,
    )
    for document in result_list:
      document = document.getObject()
      parent = document.getParentValue()
      parent.manage_delObjects(ids=[document.getId()])
    self.tic()


  def updateCreateAction(self, portal_type, action_id, action_type, action_text,
                        priority=1):
    portal_type = self.portal.portal_types[portal_type]
    action = portal_type.get(action_id, None)
    if not action:
      action = portal_type.newContent(
        portal_type="Action Information",
        id=action_id,
      )
    action.edit(
      title=action_id,
      reference=action_id,
      action=action_text,
      action_type=action_type,
      float_index=priority,
    )
    return action

  def updateCreateActionType(self, action_type):
    action_type_category = self.portal.portal_categories.action_type
    if not action_type in action_type_category:
      action_type_category.newContent(
        portal_type="Category",
        title=action_type,
        id=action_type,
      )

  def getToApi(self, json_data):
    self.portal.REQUEST.set("BODY", json_data)
    return self.web_site.api.get()

  def putToApi(self, json_data):
    self.portal.REQUEST.set("BODY", json_data)
    return self.web_site.api.put()

  def postToApi(self, json_data):
    self.portal.REQUEST.set("BODY", json_data)
    return self.web_site.api.post()

  def allDocsToApi(self, json_data):
    self.portal.REQUEST.set("BODY", json_data)
    return self.web_site.api.allDocs()

  def createActionAndActionTypeAndSetItOnApi(self, portal_type, jio_action,
                                             action_type=None, action_extra_text="",
                                             priority=None):
    if not action_type:
      action_type = "%s_%s_%s" % (self.id_template, jio_action, self.current_id)
      self.updateCreateActionType(action_type)
    action_id = "%s_action%s" % (action_type, action_extra_text)
    action = self.updateCreateAction(portal_type, action_id, action_type,
                                     "string:${object_url}/VIN_getVINAsJSON", priority)
    self.api_web_section.setProperty(
      "configuration_%s_action_type" % jio_action,
      action_type
    )
    return action

  def test_list_action_post_is_listed(self):
    """
    Test that a new post action is listed as possible action
    """
    action = self.createActionAndActionTypeAndSetItOnApi("jIO Web Section", "post")
    self.tic()
    action_list = self.web_site.api.ERP5Site_getAllActionListForAPIPost()
    self.assertEqual(len(action_list), 1)
    self.assertEqual(action, action_list[0].getObject())

  def test_list_action_post_is_not_listed(self):
    """
    If the action is not set on jIO Web Section it won't be listed
    """
    self.createActionAndActionTypeAndSetItOnApi("Person", "post")
    self.tic()
    action_list = self.web_site.api.ERP5Site_getAllActionListForAPIPost()
    self.assertEqual(len(action_list), 0)

  def test_list_action_put_is_listed(self):
    """
    Test that a new put action is listed as possible action
    """
    action = self.createActionAndActionTypeAndSetItOnApi("Person", "put")
    self.tic()
    action_list = self.web_site.api.ERP5Site_getAllActionListForAPIPut()
    self.assertEqual(len(action_list), 1)
    self.assertEqual(action, action_list[0].getObject())

  def test_list_action_get_is_listed(self):
    """
    Test that a new get action is listed as possible action
    """
    action = self.createActionAndActionTypeAndSetItOnApi("Person", "get")
    self.tic()
    action_list = self.web_site.api.ERP5Site_getAllActionListForAPIGet()
    self.assertEqual(len(action_list), 1)
    self.assertEqual(action, action_list[0].getObject())

  def test_list_action_all_docs_is_listed(self):
    """
    Test that a new allDocs action is listed as possible action
    """
    action = self.createActionAndActionTypeAndSetItOnApi("jIO Web Section", "alldocs")
    self.tic()
    action_list = self.web_site.api.ERP5Site_getAllActionListForAPIAllDocs()
    self.assertEqual(len(action_list), 1)
    self.assertEqual(action, action_list[0].getObject())

  def test_list_action_all_docs_is_not_listed(self):
    """
    If the action is not set on jIO Web Section it won't be listed
    """
    self.createActionAndActionTypeAndSetItOnApi("Person", "alldocs")
    self.tic()
    action_list = self.web_site.api.ERP5Site_getAllActionListForAPIAllDocs()
    self.assertEqual(len(action_list), 0)

  def test_json_api_hyperschema(self):
    """
    Test a basic json hyper schema
    """
    all_docs_action_type = "%s_%s_%s" % (self.id_template, "alldocs", self.current_id)
    post_action_type = "%s_%s_%s" % (self.id_template, "post", self.current_id)
    put_action_type = "%s_%s_%s" % (self.id_template, "put", self.current_id)
    get_action_type = "%s_%s_%s" % (self.id_template, "get", self.current_id)
    for action_type in [
        all_docs_action_type, post_action_type, get_action_type, put_action_type
    ]:
      self.updateCreateActionType(action_type)
    all_docs_action_list = [
      self.createActionAndActionTypeAndSetItOnApi(
        "jIO Web Section", "alldocs", action_type=all_docs_action_type, action_extra_text="_1", priority=2,
      ),
      self.createActionAndActionTypeAndSetItOnApi(
        "jIO Web Section", "alldocs", action_type=all_docs_action_type, action_extra_text="_2", priority=1,
      ),
    ]
    post_action_list = [
      self.createActionAndActionTypeAndSetItOnApi(
        "jIO Web Section", "post", action_type=post_action_type, action_extra_text="_1", priority=3,
      ),
      self.createActionAndActionTypeAndSetItOnApi(
        "jIO Web Section", "post", action_type=post_action_type, action_extra_text="_2", priority=2,
      ),
      self.createActionAndActionTypeAndSetItOnApi(
        "jIO Web Section", "post", action_type=post_action_type, action_extra_text="_3", priority=1,
      ),
    ]
    put_action_list = [
      self.createActionAndActionTypeAndSetItOnApi(
        "Person", "put", action_type=put_action_type, action_extra_text="_1", priority=2,
      ),
      self.createActionAndActionTypeAndSetItOnApi(
        "Person", "put", action_type=put_action_type, action_extra_text="_3", priority=1,
      )
    ]
    get_action_list = [
      self.createActionAndActionTypeAndSetItOnApi(
        "Person", "get", action_type=get_action_type, action_extra_text="_1", priority=3,
      ),
      self.createActionAndActionTypeAndSetItOnApi(
        "Person", "get", action_type=get_action_type, action_extra_text="_12", priority=2,
      ),
      self.createActionAndActionTypeAndSetItOnApi(
        "Person", "get", action_type=get_action_type, action_extra_text="_13", priority=1,
      ),
    ]
    self.tic()
    self.assertEqual(
      len(all_docs_action_list), len(self.web_site.api.ERP5Site_getAllActionListForAPIAllDocs())
    )
    self.assertEqual(
      len(post_action_list), len(self.web_site.api.ERP5Site_getAllActionListForAPIPost())
    )
    self.assertEqual(
      len(put_action_list), len(self.web_site.api.ERP5Site_getAllActionListForAPIPut())
    )
    self.assertEqual(
      len(get_action_list), len(self.web_site.api.ERP5Site_getAllActionListForAPIGet())
    )
    # Check Hyperschema
    base_url = self.web_site.api.absolute_url().strip("/") + "/"
    expected_hyper_schema = {
      "$schema": "https://json-schema.org/draft/2019-09/schema",
      "base": base_url,
      "links": []
    }
    expected_hyper_schema["links"] = expected_hyper_schema["links"] + [{
      "jio_type": "get",
      "href": "get/",
      "targetSchema": "get-request-schema.json",
      "title": "Get Document",
      "method": "POST",
      "curl-example":
        'curl -u user:password %s -H "Content-Type: application/json" --data @input.json' % (
          base_url + "get/",
        )
    }]
    def generateActionInputSchemaUrl(url):
      _, script = url.rsplit('/', 1)
      return base_url + script + "/getTextContent"

    def populateLinks(jio_type, url, action_list):
      result_list = []
      for action in action_list:
        result_list.append({
          "jio_type": jio_type,
          "href": url,
          "targetSchema": generateActionInputSchemaUrl(action.getActionText()),
          "title": action.getTitle(),
          "method": "POST",
          "curl-example":
            'curl -u user:password %s -H "Content-Type: application/json" --data @input.json' % (
              base_url + url,
            )
        })
      return result_list
    expected_hyper_schema["links"] = expected_hyper_schema["links"] +\
      populateLinks("post", "post/", post_action_list)
    expected_hyper_schema["links"] = expected_hyper_schema["links"] +\
      populateLinks("put", "put/", put_action_list)
    expected_hyper_schema["links"] = expected_hyper_schema["links"] +\
      populateLinks("allDocs", "allDocs/", all_docs_action_list)
    self.maxDiff = None
    self.assertEqual(
      json.dumps(expected_hyper_schema, indent=2),
      self.web_site.api.jIOWebSection_getAPIJSONHyperSchema()
    )

  def checkBadJSONPayload(self, api_method):
    """
    Test API method with bad JSON
    """
    # Send bad JSON
    json_payload = '{'
    invalid_json_error_message = "Expecting property name enclosed in double quotes: line 1 column 2 (char 1)"
    if six.PY2:
      invalid_json_error_message = u"Expecting object: line 1 column 1 (char 0)"
    result = json.loads(api_method(json_payload))
    self.assertEqual(400, result[u"status"])
    self.assertEqual(result[u"message"], invalid_json_error_message)
    self.assertEqual(u"API-JSON-INVALID-JSON", result[u"name"])
    error_record = self.portal.restrictedTraverse("error_record_module/" + (result['debug_id'] if six.PY3 else result['debug_id'].encode()))
    self.assertEqual(error_record.getDescription(), invalid_json_error_message)

    self.assertEqual(error_record.getTitle(), "API-JSON-INVALID-JSON")
    self.assertEqual(error_record.getTextContent(), json_payload)
    # Do not send a JSON object
    json_payload = '["foo", "bar"]'
    result = json.loads(api_method(json_payload))
    self.assertEqual(400, result[u"status"])
    self.assertEqual(u"API-JSON-NOT-JSON-OBJECT", result[u"name"])
    self.assertEqual(u"Did not received a JSON Object", result[u"message"])
    error_record = self.portal.restrictedTraverse("error_record_module/" + (result['debug_id'] if six.PY3 else result['debug_id'].encode()))
    self.assertEqual(error_record.getDescription(), "Did not received a JSON Object")
    self.assertEqual(error_record.getTitle(), "API-JSON-NOT-JSON-OBJECT")
    self.assertEqual(error_record.getTextContent(), json_payload)

  def createUpdateScriptPersonAsBasicJSON(self):
    createZODBPythonScript(
      self.portal.portal_skins.custom,
      "Person_asBasicJSON",
      "text_data, list_error",
      """
import json
return json.dumps({
  "id": context.getRelativeUrl(),
  "title": context.getTitle(),
}, indent=2)
"""
    )

  def test_action_get_success(self):
    """
    Test that a get action is called with success
    """
    self.createUpdateScriptPersonAsBasicJSON()
    self.updateCreateAction(
      "Person", "%sperson_get_basic_json" % self.id_template,
      self.action_type_dict["get"], "string:${object_url}/Person_asBasicJSON"
    )
    person = self.portal.person_module.newContent(
      id="%s_person" % (self.id_template,),
      portal_type="Person",
      title=self.id_template,
    )
    self.tic()
    self.assertEqual(
      self.getToApi('{"id": "%s"}' % person.getRelativeUrl()),
      json.dumps({
        "id": person.getRelativeUrl(),
        "title": person.getTitle()
      }, indent=2)
    )

  def test_action_get_document_doesnt_exists(self):
    """
    Test GET action with non-existing document
    """
    self.createUpdateScriptPersonAsBasicJSON()
    self.updateCreateAction(
      "Person", "%sperson_get_basic_json" % self.id_template,
      self.action_type_dict["get"], "string:${object_url}/Person_asBasicJSON"
    )
    self.tic()
    json_payload = '{"id": "person_module/%s_person"}' % self.id_template
    result = json.loads(self.getToApi(json_payload))
    self.assertEqual(404, result[u"status"])
    self.assertEqual(u"API-DOCUMENT-NOT-FOUND", result[u"name"])
    self.assertEqual(u"Document has not been found", result[u"message"])
    error_record = self.portal.restrictedTraverse("error_record_module/" + (result[u"debug_id"].encode() if six.PY2 else result["debug_id"]))
    self.assertEqual(error_record.getTitle(), "API-DOCUMENT-NOT-FOUND")
    self.assertEqual(error_record.getDescription(), "Document has not been found")
    self.assertEqual(error_record.getTextContent(), json_payload)


  def test_action_get_missing_id(self):
    """
    Test GET action with missing id parameter
    """
    self.createUpdateScriptPersonAsBasicJSON()
    self.updateCreateAction(
      "Person", "%sperson_get_basic_json" % self.id_template,
      self.action_type_dict["get"], "string:${object_url}/Person_asBasicJSON"
    )
    self.tic()
    json_payload = '{}'
    result = json.loads(self.getToApi(json_payload))
    self.assertEqual(400, result[u"status"])
    self.assertEqual(u"API-JSON-NO-ID-PROPERTY", result[u"name"])
    self.assertEqual(u"Cannot find id property", result[u"message"])
    error_record = self.portal.restrictedTraverse("error_record_module/" + (result[u"debug_id"].encode() if six.PY2 else result["debug_id"]))
    self.assertEqual(error_record.getTitle(), "API-JSON-NO-ID-PROPERTY")
    self.assertEqual(error_record.getDescription(), "Cannot find id property")
    self.assertEqual(error_record.getTextContent(), json_payload)

  def test_action_get_portal_type_not_listed(self):
    """
    Test GET action when action not listed on portal_type
    """
    self.createUpdateScriptPersonAsBasicJSON()
    self.tic()
    person = self.portal.person_module.newContent(
      id="%s_person" % (self.id_template,),
      portal_type="Person",
      title=self.id_template,
    )
    json_payload = '{"id": "%s"}' % person.getRelativeUrl()
    result = json.loads(self.getToApi(json_payload))
    self.assertEqual(400, result[u"status"])
    message = u"Unauthorized: No action with category %s found for %s" % (
      self.action_type_dict["get"], person.getRelativeUrl())
    self.assertEqual(u"API-NO-ACTION-FOUND", result[u"name"])
    self.assertEqual(message, result[u"message"])
    error_record = self.portal.restrictedTraverse("error_record_module/" + (result[u"debug_id"].encode() if six.PY2 else result["debug_id"]))
    self.assertEqual(error_record.getTitle(), "API-NO-ACTION-FOUND")
    self.assertEqual(error_record.getDescription(), (message.encode() if six.PY2 else message))
    self.assertEqual(error_record.getTextContent(), json_payload)

  def test_action_get_bad_json(self):
    """
    Test GET action with bad JSON
    """
    self.checkBadJSONPayload(self.getToApi)

  def createUpdateScriptPersonUpdateTitleFromJSON(self):
    createZODBPythonScript(
      self.portal.portal_skins.custom,
      "Person_updateTitleFromJSON",
      "data, list_error",
      """
import json
context.setTitle(data['title'])
return json.dumps({
  "id": context.getRelativeUrl()
}, indent=2)
"""
    )

  def test_action_put_success(self):
    """
    Test PUT action success case
    """
    self.createUpdateScriptPersonUpdateTitleFromJSON()
    self.updateCreateAction(
      "Person", "%sperson_put_basic_json" % self.id_template,
      self.action_type_dict["put"], "string:${object_url}/Person_updateTitleFromJSON"
    )
    person = self.portal.person_module.newContent(
      id="%s_person" % (self.id_template,),
      portal_type="Person",
      title=self.id_template,
    )
    self.tic()
    self.assertEqual(
      json.dumps({
        "id": person.getRelativeUrl(),
      }, indent=2),
      self.putToApi('{"id": "%s", "title": "%s"}' % (
        person.getRelativeUrl(),
        person.getRelativeUrl()
      ))
    )
    self.assertEqual(person.getTitle(), person.getRelativeUrl())

  def test_action_put_document_doesnt_exists(self):
    """
    Test PUT action with non-existing document
    """
    self.createUpdateScriptPersonUpdateTitleFromJSON()
    self.updateCreateAction(
      "Person", "%sperson_put_basic_json" % self.id_template,
      self.action_type_dict["put"], "string:${object_url}/Person_updateTitleFromJSON"
    )
    self.tic()
    json_payload = '{"id": "person_module/%s_person"}' % self.id_template
    result = json.loads(self.putToApi(json_payload))
    self.assertEqual(404, result[u"status"])
    self.assertEqual(u"API-DOCUMENT-NOT-FOUND", result[u"name"])
    self.assertEqual(u"Document has not been found", result[u"message"])
    error_record = self.portal.restrictedTraverse("error_record_module/" + (result[u"debug_id"].encode() if six.PY2 else result["debug_id"]))
    self.assertEqual(error_record.getTitle(), "API-DOCUMENT-NOT-FOUND")
    self.assertEqual(error_record.getDescription(), "Document has not been found")
    self.assertEqual(error_record.getTextContent(), json_payload)

  def test_action_put_missing_id(self):
    """
    Test PUT action with missing id parameter
    """
    self.createUpdateScriptPersonUpdateTitleFromJSON()
    self.updateCreateAction(
      "Person", "%sperson_put_basic_json" % self.id_template,
      self.action_type_dict["put"], "string:${object_url}/Person_updateTitleFromJSON"
    )
    self.tic()
    json_payload = '{}'
    result = json.loads(self.putToApi(json_payload))
    self.assertEqual(400, result[u"status"])
    self.assertEqual(u"API-JSON-NO-ID-PROPERTY", result[u"name"])
    self.assertEqual(u"Cannot find id property", result[u"message"])
    error_record = self.portal.restrictedTraverse("error_record_module/" + (result[u"debug_id"].encode() if six.PY2 else result["debug_id"]))
    self.assertEqual(error_record.getTitle(), "API-JSON-NO-ID-PROPERTY")
    self.assertEqual(error_record.getDescription(), "Cannot find id property")
    self.assertEqual(error_record.getTextContent(), json_payload)

  def test_action_put_portal_type_not_listed(self):
    """
    Test PUT action when action not listed on portal_type
    """
    self.createUpdateScriptPersonUpdateTitleFromJSON()
    person = self.portal.person_module.newContent(
      id="%s_person" % (self.id_template,),
      portal_type="Person",
      title=self.id_template,
    )
    json_payload = '{"id": "%s"}' % person.getRelativeUrl()
    result = json.loads(self.putToApi(json_payload))
    self.assertEqual(400, result[u"status"])
    message = u"Unauthorized: No action with category %s found for %s" % (
      self.action_type_dict["put"], person.getRelativeUrl())
    self.assertEqual(u"API-NO-ACTION-FOUND", result[u"name"])
    self.assertEqual(message, result[u"message"])
    error_record = self.portal.restrictedTraverse("error_record_module/" + (result[u"debug_id"].encode() if six.PY2 else result["debug_id"]))
    self.assertEqual(error_record.getTitle(), "API-NO-ACTION-FOUND")
    self.assertEqual(error_record.getDescription(), (message.encode() if six.PY2 else message))
    self.assertEqual(error_record.getTextContent(), json_payload)

  def test_action_put_bad_json(self):
    """
    Test PUT action with bad JSON
    """
    self.checkBadJSONPayload(self.putToApi)

  def createUpdateScriptjIOWebSectionCreatePersonFromJSON(self):
    createZODBPythonScript(
      self.portal.portal_skins.custom,
      "jIOWebSection_createPersonFromJSON",
      "data, list_error",
      """
import json
if not data["portal_type"] == "Person":
  raise ValueError(json.dumps({"person_creation": "Data doesn't match Person Creation"}))
person = context.getPortalObject().person_module.newContent(
  portal_type="Person",
  title=data["title"],
)
return json.dumps({
  "id": person.getRelativeUrl()
}, indent=2)
""")

  def test_action_post_success_one_action(self):
    """
    Test POST action success case
    """
    self.createUpdateScriptjIOWebSectionCreatePersonFromJSON()
    self.updateCreateAction(
      "jIO Web Section", "%sperson_post_basic_json" % self.id_template,
      self.action_type_dict["post"], "string:${object_url}/jIOWebSection_createPersonFromJSON"
    )
    self.tic()
    response = json.loads(self.postToApi(
      """{
        "portal_type": "Person",
        "title": "%s"
      }""" % self.id_template
    ))
    if not "id" in response:
      raise ValueError("Unexcpected Answer %s" % response)
    self.assertEqual(self.portal.REQUEST.RESPONSE.getStatus(), 201)
    self.portal.REQUEST.RESPONSE.setStatus(200)
    person = self.portal.restrictedTraverse(response['id'].encode() if six.PY2 else response["id"])
    self.assertEqual(person.getTitle(), self.id_template)

  def createUpdateScriptjIOWebSectionCreateOrganisationFromJSON(self):
    createZODBPythonScript(
      self.portal.portal_skins.custom,
      "jIOWebSection_createOrganisationFromJSON",
      "data, list_error",
      """
import json
if not data["portal_type"] == "Organisation":
  raise ValueError(json.dumps({"organisation_creation": "Data doesn't match Organisation Creation"}))
organisation = context.getPortalObject().organisation_module.newContent(
  portal_type="Organisation",
  title=data["title"],
)
return json.dumps({
  "id": organisation.getRelativeUrl()
}, indent=2)
""")

  def test_action_post_success_two_actions(self):
    """
    Test POST action success two action listed
    """
    self.createUpdateScriptjIOWebSectionCreateOrganisationFromJSON()
    self.updateCreateAction(
      "jIO Web Section", "%sorganisation_post_basic_json" % self.id_template,
      self.action_type_dict["post"], "string:${object_url}/jIOWebSection_createOrganisationFromJSON"
    )
    self.createUpdateScriptjIOWebSectionCreatePersonFromJSON()
    self.updateCreateAction(
      "jIO Web Section", "%sperson_post_basic_json" % self.id_template,
      self.action_type_dict["post"], "string:${object_url}/jIOWebSection_createPersonFromJSON"
    )
    self.tic()
    # Check First action
    response = json.loads(self.postToApi(
      """{
        "portal_type": "Organisation",
        "title": "%s"
      }""" % self.id_template
    ))
    if not "id" in response:
      raise ValueError("Unexcpected Answer %s" % response)
    self.assertEqual(self.portal.REQUEST.RESPONSE.getStatus(), 201)
    self.portal.REQUEST.RESPONSE.setStatus(200)
    organisation = self.portal.restrictedTraverse(response['id'].encode() if six.PY2 else response["id"])
    self.assertEqual(organisation.getTitle(), self.id_template)
    # Check Second action
    response = json.loads(self.postToApi(
      """{
        "portal_type": "Person",
        "title": "%s"
      }""" % self.id_template
    ))
    if not "id" in response:
      raise ValueError("Unexcpected Answer %s" % response)
    self.assertEqual(self.portal.REQUEST.RESPONSE.getStatus(), 201)
    self.portal.REQUEST.RESPONSE.setStatus(200)
    person = self.portal.restrictedTraverse(response['id'].encode() if six.PY2 else response["id"])
    self.assertEqual(person.getTitle(), self.id_template)

  def test_action_post_no_action_matches(self):
    """
    Test POST action, doesn't find matching action
    """
    self.createUpdateScriptjIOWebSectionCreateOrganisationFromJSON()
    self.updateCreateAction(
      "jIO Web Section", "%sorganisation_post_basic_json" % self.id_template,
      self.action_type_dict["post"], "string:${object_url}/jIOWebSection_createOrganisationFromJSON",
      priority=2
    )
    self.createUpdateScriptjIOWebSectionCreatePersonFromJSON()
    self.updateCreateAction(
      "jIO Web Section", "%sperson_post_basic_json" % self.id_template,
      self.action_type_dict["post"], "string:${object_url}/jIOWebSection_createPersonFromJSON"
    )
    self.tic()
    json_payload = """{
        "portal_type": "Image",
        "title": "%s"
      }""" % self.id_template
    result = json.loads(self.postToApi(json_payload))
    self.assertEqual(400, result[u"status"])
    details_list = sorted([
      [u'organisation_creation', u"Data doesn't match Organisation Creation"],
      [u'person_creation', u"Data doesn't match Person Creation"],
    ])
    message = u"Data did not validate against interface schemas"
    self.assertEqual(u"API-NO-ACTION-FOUND", result[u"name"])
    self.assertEqual(message, result[u"message"])
    self.assertEqual(details_list, result[u"details"])
    error_record = self.portal.restrictedTraverse("error_record_module/" + (result[u"debug_id"].encode() if six.PY2 else result["debug_id"]))
    self.assertEqual(error_record.getTitle(), "API-NO-ACTION-FOUND")
    self.assertEqual(error_record.getTextContent(), json_payload)

  def test_action_post_action_not_listed(self):
    """
    Test POST action, doesn't find matching action
    """
    self.createUpdateScriptjIOWebSectionCreateOrganisationFromJSON()
    self.updateCreateAction(
      "jIO Web Section", "%sorganisation_post_basic_json" % self.id_template,
      self.action_type_dict["post"], "string:${object_url}/jIOWebSection_createOrganisationFromJSON",
      priority=2
    )
    self.createUpdateScriptjIOWebSectionCreatePersonFromJSON()
    self.updateCreateAction(
      "Person", "%sperson_post_basic_json" % self.id_template,
      self.action_type_dict["post"], "string:${object_url}/jIOWebSection_createPersonFromJSON"
    )
    self.tic()
    json_payload = """{
        "portal_type": "Person",
        "title": "%s"
      }""" % self.id_template
    result = json.loads(self.postToApi(json_payload))
    self.assertEqual(400, result[u"status"])
    details_list = [[u'organisation_creation', u"Data doesn't match Organisation Creation"]]
    message = u"Data did not validate against interface schemas"
    self.assertEqual(u"API-NO-ACTION-FOUND", result[u"name"])
    self.assertEqual(message, result[u"message"])
    self.assertEqual(details_list, result[u"details"])
    error_record = self.portal.restrictedTraverse("error_record_module/" + (result[u"debug_id"].encode() if six.PY2 else result["debug_id"]))
    self.assertEqual(error_record.getTitle(), "API-NO-ACTION-FOUND")
    self.assertEqual(error_record.getTextContent(), json_payload)

  def test_action_post_bad_json(self):
    """
    Test POST action with bad JSON
    """
    self.checkBadJSONPayload(self.postToApi)

  def createUpdateScriptjIOWebSectionSearchPersonFromJSON(self):
    createZODBPythonScript(
      self.portal.portal_skins.custom,
      "jIOWebSection_searchPersonFromJSON",
      "data, list_error",
      """
import json
if not data["portal_type"] == "Person":
  raise ValueError(json.dumps({"person_search": "Data doesn't match Person Search"}))
search_kw = {
  "portal_type": "Person",
  "relative_url": "%%%s%%",
}
title = data.get("title", None)
if title:
  search_kw["title"] = title
result_list = context.getPortalObject().portal_catalog(
  select_list=("relative_url", "portal_type", "title"),
  **search_kw
)
return [{
  "id": x.relative_url,
  "portal_type": x.portal_type,
  "title": x.title,
} for x in result_list]
""" % (self.id_template))

  def test_action_all_docs_success_one_action_one_result(self):
    """
    Test ALLDOCS action success case
    """
    self.createUpdateScriptjIOWebSectionSearchPersonFromJSON()
    self.updateCreateAction(
      "jIO Web Section", "%sperson_all_docs_basic_json" % self.id_template,
      self.action_type_dict["alldocs"], "string:${object_url}/jIOWebSection_searchPersonFromJSON"
    )
    person = self.portal.person_module.newContent(
      id="%s_person" % (self.id_template),
      portal_type="Person",
      title=self.id_template,
    )
    self.tic()
    response = json.loads(self.allDocsToApi(
      """{
        "portal_type": "Person",
        "title": "%s"
      }""" % self.id_template
    ))
    if not "result_list" in response:
      raise ValueError("Unexcpected Answer %s" % response)
    self.assertEqual(
      response["result_list"],
      [{
        "id": person.getRelativeUrl(),
        "portal_type": person.getPortalType(),
        "title": person.getTitle(),
      }],
    )

  def test_action_all_docs_success_one_action_no_result(self):
    """
    Test ALLDOCS action success case
    """
    self.createUpdateScriptjIOWebSectionSearchPersonFromJSON()
    self.updateCreateAction(
      "jIO Web Section", "%sorganisation_all_docs_basic_json" % self.id_template,
      self.action_type_dict["alldocs"], "string:${object_url}/jIOWebSection_searchPersonFromJSON"
    )
    self.portal.person_module.newContent(
      id="%s_person" % (self.id_template),
      portal_type="Person",
      title=self.id_template,
    )
    self.tic()
    response = json.loads(self.allDocsToApi(
      """{
        "portal_type": "Person",
        "title": "BAR"
      }"""
    ))
    if not "result_list" in response:
      raise ValueError("Unexcpected Answer %s" % response)
    self.assertEqual(0, len(response["result_list"]))

  def createUpdateScriptjIOWebSectionSearchOrganisationFromJSON(self):
    createZODBPythonScript(
      self.portal.portal_skins.custom,
      "jIOWebSection_searchOrganisationFromJSON",
      "data, list_error",
      """
import json
if not data["portal_type"] == "Organisation":
  raise ValueError(json.dumps({"organisation_search": "Data doesn't match Organisation Search"}))
search_kw = {
  "portal_type": "Organisation",
  "relative_url": "%%%s_%s%%",
}
title = data.get("title", None)
if title:
  search_kw["title"] = title
result_list = context.getPortalObject().portal_catalog(
  select_list=("relative_url", "portal_type", "title"),
  **search_kw
)
return [{
  "id": x.relative_url,
  "portal_type": x.portal_type,
  "title": x.title,
} for x in result_list]
""")

  def test_action_all_docs_success_two_actions_with_result(self):
    """
    Test POST action success two action listed
    """
    self.createUpdateScriptjIOWebSectionSearchOrganisationFromJSON()
    self.updateCreateAction(
      "jIO Web Section", "%sorganisation_all_docs_basic_json" % self.id_template,
      self.action_type_dict["alldocs"], "string:${object_url}/jIOWebSection_searchOrganisationFromJSON",
      priority=2,
    )
    self.createUpdateScriptjIOWebSectionSearchPersonFromJSON()
    self.updateCreateAction(
      "jIO Web Section", "%sperson_all_docs_basic_json" % self.id_template,
      self.action_type_dict["alldocs"], "string:${object_url}/jIOWebSection_searchPersonFromJSON"
    )
    person = self.portal.person_module.newContent(
      id="%s_%s_person" % (self.id_template, self.current_id),
      portal_type="Person",
      title=self.id_template,
    )
    organisation = self.portal.organisation_module.newContent(
      id="%s_%s_organisation" % (self.id_template, self.current_id),
      portal_type="Organisation",
      title=self.id_template,
    )
    self.tic()
    # Check First action
    response = json.loads(self.allDocsToApi(
      """{
        "portal_type": "Organisation",
        "title": "%s"
      }""" % self.id_template
    ))
    if not "result_list" in response:
      raise ValueError("Unexcpected Answer %s" % response)
    self.assertEqual(
      response["result_list"],
      [{
        "id": organisation.getRelativeUrl(),
        "portal_type": organisation.getPortalType(),
        "title": organisation.getTitle(),
      }],
    )
    # Check Second action
    response = json.loads(self.allDocsToApi(
      """{
        "portal_type": "Person",
        "title": "%s"
      }""" % self.id_template
    ))
    if not "result_list" in response:
      raise ValueError("Unexcpected Answer %s" % response)
    self.assertEqual(
      response["result_list"],
      [{
        "id": person.getRelativeUrl(),
        "portal_type": person.getPortalType(),
        "title": person.getTitle(),
      }],
    )

  def test_action_all_docs_success_two_actions_with_no_result(self):
    """
    Test POST action success two action listed
    """
    self.createUpdateScriptjIOWebSectionSearchOrganisationFromJSON()
    self.updateCreateAction(
      "jIO Web Section", "%sorganisation_all_docs_basic_json" % self.id_template,
      self.action_type_dict["alldocs"], "string:${object_url}/jIOWebSection_searchOrganisationFromJSON",
      priority=2,
    )
    self.createUpdateScriptjIOWebSectionSearchPersonFromJSON()
    self.updateCreateAction(
      "jIO Web Section", "%sperson_all_docs_basic_json" % self.id_template,
      self.action_type_dict["alldocs"], "string:${object_url}/jIOWebSection_searchPersonFromJSON"
    )
    self.portal.person_module.newContent(
      id="%s_%s_person" % (self.id_template, self.current_id),
      portal_type="Person",
      title=self.id_template,
    )
    self.portal.organisation_module.newContent(
      id="%s_%s_organisation" % (self.id_template, self.current_id),
      portal_type="Organisation",
      title=self.id_template,
    )
    self.tic()
    # Check First action
    response = json.loads(self.allDocsToApi(
      """{
        "portal_type": "Organisation",
        "title": "BAR"
      }"""
    ))
    if not "result_list" in response:
      raise ValueError("Unexcpected Answer %s" % response)
    self.assertEqual(0, len(response["result_list"]))
    # Check Second action
    response = json.loads(self.allDocsToApi(
      """{
        "portal_type": "Person",
        "title": "BAR"
      }"""
    ))
    if not "result_list" in response:
      raise ValueError("Unexcpected Answer %s" % response)
    self.assertEqual(0, len(response["result_list"]))

  def test_action_all_docs_no_action_matches(self):
    """
    Test POST action, doesn't find matching action
    """
    self.createUpdateScriptjIOWebSectionSearchOrganisationFromJSON()
    self.updateCreateAction(
      "jIO Web Section", "%sorganisation_all_docs_basic_json" % self.id_template,
      self.action_type_dict["alldocs"], "string:${object_url}/jIOWebSection_searchOrganisationFromJSON",
      priority=2,
    )
    self.createUpdateScriptjIOWebSectionSearchPersonFromJSON()
    self.updateCreateAction(
      "jIO Web Section", "%sperson_all_docs_basic_json" % self.id_template,
      self.action_type_dict["alldocs"], "string:${object_url}/jIOWebSection_searchPersonFromJSON"
    )
    self.tic()
    json_payload = """{
        "portal_type": "Image",
        "title": "%s"
      }""" % self.id_template
    result = json.loads(self.allDocsToApi(json_payload))
    self.assertEqual(400, result[u"status"])
    details = [
      [u'organisation_search', u"Data doesn't match Organisation Search"],
      [u'person_search', u"Data doesn't match Person Search"],
    ]
    message = u"Data did not validate against interface schemas"
    self.assertEqual(u"API-NO-ACTION-FOUND", result[u"name"])
    self.assertEqual(message, result[u"message"])
    self.assertEqual(details, result[u"details"])
    error_record = self.portal.restrictedTraverse("error_record_module/" + (result[u"debug_id"].encode() if six.PY2 else result["debug_id"]))
    self.assertEqual(error_record.getTitle(), "API-NO-ACTION-FOUND")
    self.assertEqual(error_record.getTextContent(), json_payload)

  def test_action_all_docs_action_not_listed(self):
    """
    Test POST action, doesn't find matching action
    """
    self.createUpdateScriptjIOWebSectionSearchOrganisationFromJSON()
    self.updateCreateAction(
      "jIO Web Section", "%sorganisation_all_docs_basic_json" % self.id_template,
      self.action_type_dict["alldocs"], "string:${object_url}/jIOWebSection_searchOrganisationFromJSON",
      priority=2,
    )
    self.createUpdateScriptjIOWebSectionSearchPersonFromJSON()
    self.updateCreateAction(
      "Person", "%sperson_all_docs_basic_json" % self.id_template,
      self.action_type_dict["alldocs"], "string:${object_url}/jIOWebSection_searchPersonFromJSON"
    )
    self.tic()
    json_payload = """{
        "portal_type": "Person",
        "title": "%s"
      }""" % self.id_template
    result = json.loads(self.allDocsToApi(json_payload))
    self.assertEqual(400, result[u"status"])
    details_list =[[u'organisation_search', u"Data doesn't match Organisation Search"]]
    message = u"Data did not validate against interface schemas"
    self.assertEqual(u"API-NO-ACTION-FOUND", result[u"name"])
    self.assertEqual(message, result[u"message"])
    self.assertEqual(details_list, result[u"details"])
    error_record = self.portal.restrictedTraverse("error_record_module/" + (result[u"debug_id"].encode() if six.PY2 else result["debug_id"]))
    self.assertEqual(error_record.getTitle(), "API-NO-ACTION-FOUND")
    self.assertEqual(error_record.getTextContent(), json_payload)

  def test_action_all_docs_bad_json(self):
    """
    Test POST action with bad JSON
    """
    self.checkBadJSONPayload(self.allDocsToApi)
