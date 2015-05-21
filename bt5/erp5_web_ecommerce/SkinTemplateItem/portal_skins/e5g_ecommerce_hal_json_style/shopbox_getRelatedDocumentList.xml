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
            <key> <string>_Cacheable__manager_id</string> </key>
            <value>
              <none/>
            </value>
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
            <value> <string>import json\n
if REQUEST is None:\n
  REQUEST = context.REQUEST\n
\n
# raise ValueError(\'foo\')\n
document = context.getObject()\n
\n
subobject_list = document.Base_getRelatedDocumentList()\n
subobject_result_list = []\n
\n
      \n
for subobject in subobject_list:\n
  subobject_dict = {}\n
  subobject_type = subobject.getPortalType()\n
  subobject_title = subobject.getTitle()\n
\n
  if subobject_type == \'Sale Supply Line\':\n
    pass\n
  elif subobject_type == \'Product Individual Variation\':\n
    subobject_dict[\'title\'] = subobject.getTitle()\n
  elif subobject_title == \'default_image\':\n
    subobject_dict[\'default_image_url\'] = subobject.getPath()\n
  elif subobject_type == \'Embedded File\':\n
    subobject_dict[\'image_url\'] = subobject.getPath()\n
  elif subobject_type == \'Purchase Supply Line\':\n
    subobject_dict[\'price\'] = subobject.getBasePrice()\n
  subobject_result_list.append(subobject_dict)\n
        \n
return json.dumps({\n
  # \'variation_list\': [x[0] for x in document.getVariationCategoryItemList()]\n
  \'related_document_list\': subobject_result_list\n
}, indent=2)\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>REQUEST=None</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>shopbox_getRelatedDocumentList</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
