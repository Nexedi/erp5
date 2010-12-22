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
            <value> <string encoding="cdata"><![CDATA[

# export_only : allow to disable the uid column and the id of columns\n
result = \'\'\n
request = context.REQUEST\n
\n
translate = context.portal_url.getPortalObject().Localizer.erp5_ui.gettext\n
\n
listboxline_list = context.get_value(\'default\', render_format=\'list\', REQUEST=request)\n
\n
def encode(value):\n
  if isinstance(value, bool):\n
    return \'"%s"\' % value\n
  if isinstance(value, (int, long, float)):\n
    return str(value)\n
  else:\n
    if isinstance(value, str):\n
      value = value.decode(\'utf-8\')\n
    else:\n
      value = str(value)\n
    return \'"%s"\' % value.replace(\'"\', \'""\')\n
\n
for listboxline in listboxline_list:\n
  if listboxline.isTitleLine():\n
    line_result = \'\'\n
    line_result2 = \'\'\n
\n
    if not export_only:\n
      listboxline.setListboxLineDisplayListMode([\'uid\'])  #XXX do not display uid column\n
\n
    for column_item in listboxline.getColumnItemList():\n
\n
      column_id = column_item[0]\n
      column_property = column_item[1]\n
\n
      if column_id is not None:\n
        line_result += encode(column_id)\n
      line_result += str(\',\')\n
\n
      if column_property is not None:\n
        line_result2 += encode(column_property)\n
      line_result2 += str(\',\')\n
\n
    if len(line_result) > 1:\n
      line_result = line_result[:-1]\n
\n
    if len(line_result2) > 1:\n
      line_result2 = line_result2[:-1]\n
\n
    if not export_only:\n
      result += line_result+\'\\n\' #XXX do not display id\n
    result += line_result2+\'\\n\'\n
\n
\n
\n
\n
  if listboxline.isDataLine():\n
    line_result = \'\'\n
\n
    if not export_only:\n
      listboxline.setListboxLineDisplayListMode([\'uid\'])  #XXX do not display uid column\n
\n
    for column_property in listboxline.getColumnPropertyList():\n
\n
      if column_property is not None:\n
        line_result += encode(column_property)\n
      line_result += str(\',\')\n
\n
    if len(line_result) > 1:\n
      line_result = line_result[:-1]\n
\n
    result += line_result+\'\\n\'\n
\n
return result\n


]]></string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>export_only=0,**kw</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>Listbox_exportCsv</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
