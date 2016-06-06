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
            <value> <string>from Products.ERP5Type.Document import newTempBase\n
from string import zfill\n
\n
num = 0\n
listbox_lines = []\n
\n
request = context.REQUEST\n
\n
# Get spreadsheet data\n
try:\n
  spreadsheets = request[\'ooo_import_spreadsheet_data\']\n
except KeyError:\n
  return []\n
\n
for spreadsheet in spreadsheets.keys():\n
  # In the case of empty spreadsheet do nothing\n
  if spreadsheets[spreadsheet] not in (None, []):\n
    column_name_list = spreadsheets[spreadsheet][0]\n
\n
    for column in column_name_list:\n
      safe_id = context.Base_getSafeIdFromString(\'%s%s\' % (spreadsheet, column))\n
      num += 1\n
      # int_len is used to fill the uid of the created object like 0000001\n
      int_len = 7\n
      o = newTempBase(context, safe_id)\n
      o.setUid(\'new_%s\' % zfill(num, int_len)) # XXX There is a security issue here\n
      o.edit(uid=\'new_%s\' % zfill(num, int_len)) # XXX There is a security issue here\n
      o.edit(\n
          id=safe_id,\n
          spreadsheet_name=spreadsheet,\n
          spreadsheet_column=column\n
      )\n
      listbox_lines.append(o)\n
  \n
return listbox_lines\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>**kw</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>Base_getSpreadsheetColumnNameList</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
