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
total_line = int(kw.get(\'total_line\',\'0\')) or int(request.get(\'total_line\',\'0\'))\n
title = kw.get(\'rss_title\', None) or request.get(\'rss_title\',\'No title\')\n
portal_selection = getattr(context,\'portal_selections\')\n
selection = portal_selection.getSelectionFor(kw.get(\'selection_name\',None) or request.get(\'selection_name\',\'\'))\n
params = selection.getParams()\n
readItemList = params.get(\'rss_read_item:list\', {})\n
readItemCount = len(readItemList)\n
unreadItemCount = total_line - readItemCount\n
if unreadItemCount > 0:\n
  return title +\' (\'+str(unreadItemCount)+\')\'\n
return title\n


]]></string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>**kw</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>Base_formatRssTitleWithUnreadItemCount</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
