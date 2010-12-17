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
            <value> <string>"""\n
  Allow to reuse an existing user from another instance.\n
"""\n
translateString = context.Base_translateString\n
portal = context.getPortalObject()\n
request = context.REQUEST\n
\n
kw = {}\n
kw[\'start_date\'] = request.get(\'start_date\', None)\n
kw[\'stop_date\'] = request.get(\'stop_date\', None)\n
kw[\'group\'] = request.get(\'field_my_group\', None)\n
kw[\'function\'] = request.get(\'field_my_function\', None)\n
kw[\'activity\'] = request.get(\'field_my_activity\', None)\n
kw[\'title\'] = request.get(\'field_my_title\', None)\n
kw[\'description\'] = request.get(\'field_my_description\', None)\n
\n
# XXX(lucas): Remove DateTime, because XML-RPC can not handle it.\n
request.form[\'start_date\'] = ""\n
request.REQUEST.form[\'stop_date\'] = ""\n
\n
if context.getReference():\n
  portal_status_message = translateString(\'User has login already.\')\n
elif not context.WizardTool_isPersonReferencePresent(reference):\n
  portal_status_message = translateString(\'User does not exist yet.\')\n
else:\n
  # create a local copy\n
  context.edit(reference=reference)\n
\n
  # create local assignment\n
  tag = \'%s_reuse_create_assignment\' % context.getId()\n
  context.activate(tag=tag).Person_createAssignment(**kw)\n
\n
  # create a global account\n
  if 1:#portal.portal_wizard.isSingleSignOnEnabled():\n
    context.activate(after_tag=tag).Person_synchroniseExistingAccountWithInstance()\n
\n
  # create a global account\n
  context.Person_synchroniseExistingAccountWithInstance()\n
  portal_status_message = translateString(\'Status changed.\')\n
\n
# redirect appropriately\n
context.Base_redirect(form_id=form_id,\n
                      keep_items={\'portal_status_message\': portal_status_message})\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>reference, form_id=\'view\'</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>Person_reuseExistingUserAction</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
