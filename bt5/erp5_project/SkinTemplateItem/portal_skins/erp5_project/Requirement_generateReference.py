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
This script is called to generate references for all requirements\n
"""\n
\n
translateString = context.Base_translateString\n
request = context.REQUEST\n
current_type = context.getPortalType()\n
if not reference: reference=\'R\'\n
\n
def generateReference(prefix, order, portal_type):\n
  for order_line in order.contentValues(portal_type=portal_type, checked_permission=\'View\', sort_on=\'int_index\'):\n
    new_prefix = "%s-%s" % (prefix, order_line.getIntIndex(order_line.getId()))\n
    generateReference(new_prefix, order_line, portal_type)\n
    order_line.setReference(new_prefix)\n
\n
generateReference(reference, context, "Requirement")\n
\n
msg = translateString(\'Reference generated for all requirements.\')\n
\n
# Return to view mode\n
return context.Base_redirect(form_id, keep_items = {\'portal_status_message\' : msg},  **kw)\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>dialog_id=None, form_id=\'view\', reference=None, **kw</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>Requirement_generateReference</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
