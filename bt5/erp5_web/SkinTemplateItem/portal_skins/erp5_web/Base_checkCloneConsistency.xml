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
  Currently it is not possible to change it to checkConsistency.\n
  If it added similar constraints at Documents will break archive \n
  behaviour. \n
"""\n
form_data = context.REQUEST.form\n
translateString =  context.Base_translateString\n
\n
if clone:\n
  portal_type = context.getPortalType()\n
else:\n
  portal_type = form_data[\'clone_portal_type\']\n
\n
# prepare query params\n
kw = {\'portal_type\' : portal_type}\n
kw[\'reference\'] = form_data.get(\'clone_reference\') or \'\'\n
kw[\'version\'] = form_data.get(\'clone_version\') or \'\'\n
kw[\'language\'] = form_data.get(\'clone_language\') or \'\'\n
\n
# Count documents of same reference and prepare kw\n
count = int(context.portal_catalog.countResults(**kw)[0][0])\n
\n
if count:\n
  return translateString("Sorry, a ${portal_type} with reference \'${reference}\' and version \'${version} [${language}]\' already exists. Please select another reference or version.", mapping = kw)\n
\n
return None\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>clone=1, **kw</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>Base_checkCloneConsistency</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
