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
get related object value list in a security-aware way (without throwing exception\n
if I don\'t have permissions to access the object)\n
"""\n
\n
category_list = context.getPropertyList(base_category)\n
if category_list is None:\n
  return []\n
\n
def getValueIfAvailable(category):\n
  ob = context.restrictedTraverse(category, None)\n
  return ob \n
\n
object_list = [getValueIfAvailable(category) for category in category_list]\n
object_list = [o for o in object_list if o is not None]\n
\n
if portal_type_list is not None:\n
  object_list = [o for o in object_list if o.portal_type in portal_type_list]\n
\n
return object_list\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>base_category, portal_type_list=None</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>Base_getRelatedObjectValueList</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
