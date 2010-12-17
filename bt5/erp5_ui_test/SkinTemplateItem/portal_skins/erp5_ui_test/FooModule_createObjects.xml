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
            <value> <string>"""Create objects with given parameters"""\n
from DateTime import DateTime\n
category_list = (\'a\', \'b\', \'a/a1\', \'a/a2\')\n
big_category_list = (\'c1\', \'c10\', \'c2\', \'c20\', \'c3\', \'c4\')\n
\n
for i in range(start, start + num):\n
  category = category_list[i % len(category_list)]\n
  foo = context.newContent(id = str(i), title = \'Title %d\' % i, quantity = 10.0 - float(i),\n
                    foo_category = category, portal_type=portal_type)\n
  if set_dates:\n
    foo.setStartDate(DateTime(i, i, i))\n
  if create_line:\n
    foo.newContent()\n
  if big_category_related:\n
    big_category = big_category_list[i %len(category_list)]\n
    foo.setFooBigCategory(big_category)\n
\n
return \'Created Successfully.\'\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>start=0, num=10, set_dates=0, portal_type=\'Foo\', create_line=0, big_category_related=False</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>FooModule_createObjects</string> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string>Create Objects</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
