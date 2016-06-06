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
            <value> <string>portal = context.getPortalObject()\n
\n
if context.cb_dataValid:\n
  object_list = context.cb_dataItems()\n
  try:\n
    portal_type_set = set(x.getPortalType() for x in object_list)\n
  except AttributeError:\n
    error_message = \'Sorry, you can not paste these items here.\'\n
  else:\n
    if portal_type_set.issubset(context.getVisibleAllowedContentTypeList()):\n
      try:\n
        new_item_list = context.manage_pasteObjects(portal.REQUEST[\'__cp\'])\n
      except KeyError:\n
        error_message = \'Nothing to paste.\'\n
      else:\n
        #new_id_list = [i[\'new_id\'] for i in new_item_list]\n
        error_message = \'Items paste in progress.\'\n
    else:\n
      error_message = \'Sorry, you can not paste these items here.\'\n
else:\n
  error_message = \'Copy or cut one or more items to paste first.\'\n
return context.Base_redirect(form_id, keep_items=dict(\n
  portal_status_message=portal.Base_translateString(error_message)))\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>form_id</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>Folder_paste</string> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string>Paste objects to a folder from the clipboard</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
