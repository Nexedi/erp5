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

request = context.REQUEST\n
stool = context.portal_selections\n
\n
if stool.getSelectionInvertModeFor(selection_name):\n
  # if already in invert mode, toggle invert mode\n
  stool.setSelectionInvertModeFor(selection_name, invert_mode=0)\n
else:\n
  # Set selection to currently checked items, taking into consideration changes\n
  # in uids\n
  selection_uids = stool.getSelectionCheckedUidsFor(\n
                                  selection_name, REQUEST=request)\n
  filtered_uid_dict = {}\n
  listbox_uid = map(lambda x:int(x), listbox_uid)\n
  uids = map (lambda x:int(x), uids)\n
  for uid in uids:\n
     filtered_uid_dict[uid] = 1\n
  for uid in selection_uids:\n
    if uid in listbox_uid:\n
      if uid in uids:\n
        filtered_uid_dict[uid] = 1\n
    else:\n
      filtered_uid_dict[uid] = 1\n
\n
  if len(filtered_uid_dict.keys()) > 0 :\n
    stool.checkAll(selection_name, uids, REQUEST=None)\n
    stool.setSelectionToIds(selection_name,\n
                              filtered_uid_dict.keys(), REQUEST=request)\n
\n
url = stool.getSelectionListUrlFor(\n
                        selection_name, REQUEST=request)\n
request.RESPONSE.redirect(url)\n


]]></string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>selection_name, uids=[], listbox_uid=[]</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>Folder_filter</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
