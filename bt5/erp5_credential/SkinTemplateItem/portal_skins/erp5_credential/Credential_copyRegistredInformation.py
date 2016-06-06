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
            <value> <string>"""Copy information from context to an object\n
Parameters:\n
destination -- Object where copy property value\n
mapping -- Define property mapping (List of tuple of 2 property)\n
copy_none_value -- Copy or not None value of context to destination\n
erase_empty_value -- Erase or not empty value of destination"""\n
def getAccessor(property):\n
  return "".join([x.capitalize() for x in property.split(\'_\')])\n
\n
def copyValue(source_document, source_accessor,\n
              destination_document, destination_accessor):\n
    getter = getattr(source_document, \'get%s\' % source_accessor)\n
    value = getter()\n
    if value is None and copy_none_value or value is not None:\n
      old_getter = getattr(destination_document, \'get%s\' % destination_accessor)     \n
      old_value = old_getter()\n
      if not old_value and erase_empty_value or old_value: \n
        setter = getattr(destination_document, \'set%s\' % destination_accessor)\n
        setter(value)\n
\n
def copyDocument(source_document, destination_document, mapping):\n
    for source_property, destination_property in mapping:\n
        source_accessor, destination_accessor = getAccessor(source_property), getAccessor(destination_property)\n
        copyValue(source_document, source_accessor,\n
                  destination_document, destination_accessor)\n
\n
\n
\n
copyDocument(context, destination, mapping)\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>destination,mapping,copy_none_value=True,erase_empty_value=True</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>Credential_copyRegistredInformation</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
