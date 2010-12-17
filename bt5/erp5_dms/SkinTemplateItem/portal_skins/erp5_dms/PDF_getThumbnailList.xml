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
  THis script returns a suitable slide list of PDF thumbnails\n
  for current form selection.\n
  It\'s to be used in a listbox.\n
"""\n
from Products.ERP5Type.Document import newTempBase\n
\n
content_information = context.getContentInformation()\n
page_number = int(content_information.get(\'Pages\', 0))\n
limit = kw.get(\'limit\', (0, 0))\n
list_start = int(kw.get(\'list_start\', 0))\n
list_lines = int(kw.get(\'list_lines\', 0))\n
size = list_lines or limit[1]\n
\n
list_end = list_start + size\n
page_list = range(page_number)\n
\n
result = []\n
for i in page_list[list_start:list_end]:\n
  x = {\'title\': \'%s\' %i, \n
       \'frame\':\'%s\' %i} # frame is used by listbox render field\n
  temp_object = newTempBase(context, x[\'title\'], **x)\n
  result.append(temp_object)\n
return result\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>**kw</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>PDF_getThumbnailList</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
