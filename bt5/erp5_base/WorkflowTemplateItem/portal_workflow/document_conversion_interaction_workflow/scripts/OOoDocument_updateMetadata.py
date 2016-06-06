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
when OOoDocument is edited, we update metadata in the ODF file\n
\n
XXX - This script must be verified, written with clean syntax\n
"""\n
document = state_change[\'object\']\n
kw = state_change[\'kwargs\']\n
\n
# key is a name of erp5 field.\n
# value is a name of document metadata.\n
metadata_field_mapping_dict = document.getMetadataMappingDict()\n
\n
# edit metadata (only if we have OOo file)\n
if document.hasBaseData():\n
  new_metadata = {}\n
  for field in metadata_field_mapping_dict.keys():\n
    value = kw.get(field, None)\n
    if value is None:\n
      value = kw.get(\'%s_list\' % field, None)\n
    if value is not None:\n
      metadata_key = metadata_field_mapping_dict[field]\n
      new_metadata[metadata_key] = value\n
  if new_metadata:\n
    # edit metadata via server\n
    after_tag = \'document_%s_convert\' % document.getPath()\n
    document.activate(after_tag=after_tag).Document_tryToUpdateBaseMetadata(**new_metadata)\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>state_change</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>OOoDocument_updateMetadata</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
