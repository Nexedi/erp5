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
  this script is the conductor. All other scripts that permit to create a \n
  paysheet are called here\n
\'\'\'\n
import pprint\n
\n
# Delete all objects in the paysheet\n
id_list = []\n
for paysheet_item in context.objectValues(portal_type= \\\n
  [\'Pay Sheet Transaction Line\', \'Pay Sheet Line\']):\n
  # Delete lines which now became outdated and keep the sub-objects\n
  id_list.append(paysheet_item.getId())\n
context.manage_delObjects(id_list)\n
\n
# create Pay Sheet Lines\n
context.createPaySheetLineList(listbox=listbox)\n
\n
if not(kw.has_key(\'skip_redirect\') and kw[\'skip_redirect\'] == True):\n
  # Return to pay sheet default view\n
  from ZTUtils import make_query\n
  redirect_url = \'%s/%s?%s\' % (context.absolute_url(), \'view\', make_query())\n
  return context.REQUEST.RESPONSE.redirect(redirect_url)\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>listbox=[], **kw</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>PaySheetTransaction_createAllPaySheetLineList</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
