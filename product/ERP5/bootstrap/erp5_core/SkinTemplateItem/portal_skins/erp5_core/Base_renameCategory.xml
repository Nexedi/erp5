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
            <value> <string>new_category_list = ()\n
from_cat = from_cat + \'/\'\n
to_cat = to_cat + \'/\'\n
has_changed = 0\n
\n
if from_cat is not None and to_cat is not None:\n
  for o in context.objectValues():\n
    has_changed = 0\n
    new_category_list = ()\n
    for cat in o.getCategoryList():\n
      if cat.find(from_cat) == 0:\n
        cat = to_cat + cat[len(from_cat):]\n
        has_changed = 1\n
      new_category_list += (cat,)\n
    if has_changed == 1:\n
      o.setCategoryList(new_category_list)\n
      print "changed category %s with %s on %s" % (str(from_cat),str(to_cat),str(o.getPath()))\n
\n
\n
print " "\n
return printed\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>from_cat = None, to_cat = None</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>Base_renameCategory</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
