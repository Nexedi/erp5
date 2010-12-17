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
            <value> <string>apparel_model = context\n
result = \'\'\n
\n
apparel_cloth_list = apparel_model.getValueList(\'specialise\',portal_type=[\'Apparel Cloth\'])\n
apparel_shape = apparel_model.getDefaultValue(\'specialise\',portal_type=[\'Apparel Shape\'])\n
\n
object_list = []\n
\n
if apparel_shape != None:\n
  object_list.append(apparel_shape)\n
\n
object_list += apparel_cloth_list\n
\n
for object in object_list:\n
  nomenclature_tmp = object.getBillOfMaterialDescription(\'\')\n
  if nomenclature_tmp != \'\':\n
    result += nomenclature_tmp+\'\\n\'\n
\n
return result\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>ApparelModel_getAggregatedBillOfMaterialDescription</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
