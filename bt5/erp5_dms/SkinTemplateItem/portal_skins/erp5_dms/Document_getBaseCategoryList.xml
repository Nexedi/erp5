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
we return only those base categories to which all Document-related portal_types belong\n
you need to define the list of Document types here\n
and to add a base category to it in DMSFile property sheets\n
or manually for all these portal_types\n
"""\n
\n
type_list = context.getPortalDocumentTypeList()\n
nr_of_types = len(type_list)\n
\n
basecatdict = {}\n
\n
for type in type_list:\n
  type_base_cat_list = context.portal_types[type].getInstanceBaseCategoryList()\n
  for base_cat in type_base_cat_list:\n
    basecatdict[base_cat] = basecatdict.setdefault(base_cat, 0)+1\n
\n
basecatlist = [k for k,v in basecatdict.items() if v == nr_of_types]\n
basecatlist.sort()\n
return basecatlist\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>Document_getBaseCategoryList</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
