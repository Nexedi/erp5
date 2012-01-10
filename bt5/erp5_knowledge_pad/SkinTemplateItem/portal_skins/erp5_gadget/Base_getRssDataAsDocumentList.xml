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

from Products.ERP5Type.Document import newTempBase\n
from Products.ERP5Type.Cache import CachingMethod\n
\n
request = context.REQUEST\n
box_relative_url = kw.get(\'box_relative_url\')\n
selection_name = kw.get(\'list_selection_name\')\n
portal_selection = getattr(context,\'portal_selections\')\n
selection = portal_selection.getSelectionFor(selection_name)\n
\n
error_mapping_dict = {-1: \'Please enter a valid Rss or Atom url in the preference form.\',\n
                      -2: \'Wrong Rss or Atom url or service temporary down.\',\n
                      -3: \'Unauthorized, verify your authentication.\',\n
                      -4: \'Page not found.\',\n
                      -5: \'Mismatched RSS feed.\'}\n
\n
if box_relative_url:\n
  box = context.restrictedTraverse(box_relative_url)\n
  preferences = box.KnowledgeBox_getDefaultPreferencesDict()\n
else:\n
  preferences = {}\n
\n
feed_url = str(preferences.get(\'preferred_rss_feed\',\'\'))\n
username = str(preferences.get(\'preferred_username\',\'\'))\n
password = str(preferences.get(\'preferred_password\',\'\'))\n
\n
Base_getRssDataAsDict = CachingMethod(context.Base_getRssDataAsDict, \n
                                     (feed_url, username, password), cache_factory=\'erp5_ui_short\')\n
results = Base_getRssDataAsDict(context, url = feed_url, username = username, password = password)\n
\n
md5_list = []\n
message_list = []\n
items = results.get(\'items\', [])\n
status = results.get(\'status\', 0)\n
\n
context.REQUEST.set(\'rss_status\', status)\n
if status < 0:\n
  # some error occured show message to user\n
  request.set(\'rss_title\', context.Base_translateString(error_mapping_dict[status]))\n
  return []\n
else:\n
  # all good\n
  rss_title = results.get(\'title\',\'\')\n
  rss_logo = results.get(\'logo\', None)\n
  if items is not None:\n
    rss_title = \'%s (%s)\' %(rss_title, len(items))\n
  if rss_logo not in (\'\', None):\n
    request.set(\'rss_logo\', rss_logo)\n
  request.set(\'rss_link\', results.get(\'link\',None))\n
  request.set(\'rss_gadget_title\', rss_title)\n
\n
for result in items:\n
  md5_list.append(result[\'md5\'])\n
  date = context.Base_getDiffBetweenDateAndNow(result.get(\'date\',None))\n
  message = newTempBase(context, \'item\')\n
  message.edit(field_title = result.get(\'title\',\'No title\'),\n
            field_date = date,\n
            field_content = result.get(\'content\',\'No content\'),\n
            field_img = result.get(\'img\',\'\'),\n
            field_others_links = result.get(\'other_links\',\'\'),\n
            field_link = result.get(\'link\',\'\'),\n
            field_md5 = result.get(\'md5\',\'\'))\n
  message_list.append(message)\n
\n
return message_list\n


]]></string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>**kw</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>Base_getRssDataAsDocumentList</string> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string>Take Rss dictionary and return document list</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
