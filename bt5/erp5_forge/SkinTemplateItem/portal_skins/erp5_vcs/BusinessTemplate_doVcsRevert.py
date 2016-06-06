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
            <value> <string>other_file_list = []\n
if modified != \'none\':\n
  other_file_list += modified.split(\',\')\n
if removed != \'none\':\n
  other_file_list += removed.split(\',\')\n
\n
added_file_list = added != \'none\' and added.split(\',\') or ()\n
\n
if added_file_list or other_file_list:\n
  context.getVcsTool().revertZODB(added_file_list=added_file_list, other_file_list=other_file_list)\n
  context.REQUEST.set(\'portal_status_message\', \'Changes reverted successfully.\')\n
else:\n
  context.REQUEST.set(\'portal_status_message\', \'Nothing to revert.\')\n
\n
return context.BusinessTemplate_viewVcsStatus()\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>added=\'\', modified=\'\', removed=\'\', **kw</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>BusinessTemplate_doVcsRevert</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
