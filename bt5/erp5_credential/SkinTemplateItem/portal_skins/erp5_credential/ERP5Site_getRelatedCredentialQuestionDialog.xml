<?xml version="1.0"?>
<ZopeData>
  <record id="1" aka="AAAAAAAAAAE=">
    <pickle>
      <global name="PythonScript" module="Products.PythonScripts.PythonScript"/>
    </pickle>
    <pickle>
      <dictionary>
        <item>
            <key> <string>Script_magic</string> </key>
            <value> <int>3</int> </value>
        </item>
        <item>
            <key> <string>_bind_names</string> </key>
            <value>
              <object>
                <klass>
                  <global name="NameAssignments" module="Shared.DC.Scripts.Bindings"/>
                </klass>
                <tuple/>
                <state>
                  <dictionary>
                    <item>
                        <key> <string>_asgns</string> </key>
                        <value>
                          <dictionary>
                            <item>
                                <key> <string>name_container</string> </key>
                                <value> <string>container</string> </value>
                            </item>
                            <item>
                                <key> <string>name_context</string> </key>
                                <value> <string>context</string> </value>
                            </item>
                            <item>
                                <key> <string>name_m_self</string> </key>
                                <value> <string>script</string> </value>
                            </item>
                            <item>
                                <key> <string>name_subpath</string> </key>
                                <value> <string>traverse_subpath</string> </value>
                            </item>
                          </dictionary>
                        </value>
                    </item>
                  </dictionary>
                </state>
              </object>
            </value>
        </item>
        <item>
            <key> <string>_body</string> </key>
            <value> <string>\'\'\'\n
  Try to find the question related to the user passed in parameter.\n
  Proxy : this required a manager proxy role to be able to search in all persons\n
\'\'\'\n
portal = context.getPortalObject()\n
person_module = portal.getDefaultModule(\'Person\')\n
request  = context.REQUEST\n
web_site = context.getWebSiteValue()\n
if web_site:\n
  request.set("came_from", web_site.absolute_url())\n
if choice == "password":\n
  request.set(\'reference\', reference)\n
  portal_preferences = context.portal_preferences\n
  result = person_module.searchFolder(reference={\'query\': reference, \'key\': \'ExactMatch\'})\n
  if len(result) != 1:\n
    portal_status_message = context.Base_translateString("Could not find your user account.")\n
    if web_site:\n
      return web_site.Base_redirect(\'login_form\', keep_items = dict(portal_status_message=portal_status_message ))\n
    return portal.Base_redirect(\'login_form\', keep_items = dict(portal_status_message=portal_status_message ))\n
\n
  person = result[0]\n
\n
  #If any question, we can create directly the credential recovery\n
  question_free_text = person.getDefaultCredentialQuestionQuestionFreeText()\n
  question_title = person.getDefaultCredentialQuestionQuestionTitle()\n
\n
  if not (question_free_text or question_title) or \\\n
    not portal_preferences.isPreferredAskCredentialQuestion():\n
    return context.ERP5Site_newCredentialRecovery(reference=reference)\n
\n
  web_section = context.getWebSectionValue()\n
  if web_section is not None:\n
    return web_section.Base_redirect(\'question\',\n
                               keep_items = \\\n
                                  dict(default_credential_question_question_free_text=question_free_text,\n
                                      default_credential_question_question_title=question_title,\n
                                      reference=reference))\n
  else:\n
    return context.Base_redirect(\'ERP5Site_newCredentialRecoveryDialog\',\n
                               keep_items = \\\n
                                  dict(default_credential_question_question_free_text=question_free_text,\n
                                      default_credential_question_question_title=question_title,\n
                                      reference=reference))\n
elif choice == "username":\n
  query_kw = {"email.url_string" : default_email_text}\n
  result = portal.portal_catalog(portal_type="Email", parent_portal_type="Person", **query_kw)\n
  person_list = [x.getParentValue() for x in result]\n
  person_list = [x for x in person_list if x.getReference()] # only consider persons with a valid login\n
  if len(person_list) == 0:\n
    portal_status_message = context.Base_translateString("Could not find your user account.")\n
    if web_site:\n
      return web_site.Base_redirect(\'login_form\', keep_items = dict(portal_status_message=portal_status_message ))\n
    return portal.Base_redirect(\'login_form\', keep_items = dict(portal_status_message=portal_status_message ))\n
  return context.ERP5Site_newCredentialRecovery(default_email_text=default_email_text, person_list=person_list)\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>choice=\'password\', default_email_text=None, reference=None, **kw</string> </value>
        </item>
        <item>
            <key> <string>_proxy_roles</string> </key>
            <value>
              <tuple>
                <string>Manager</string>
              </tuple>
            </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>ERP5Site_getRelatedCredentialQuestionDialog</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
