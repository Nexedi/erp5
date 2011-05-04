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
            <value> <string># Look at all items availables for the source and then\n
# display them on a listbox so that the user will be able\n
# to select them\n
request = context.REQUEST\n
item_portal_type_list = ["Checkbook","Check"]\n
node = context.getBaobabSource()\n
\n
fast_input_type = getattr(request, \'your_fast_input_type\', None)\n
if fast_input_type is None:\n
  fast_input_type = getattr(request, \'field_your_fast_input_type\')\n
\n
disable_node = 0\n
at_date = context.getStartDate()\n
\n
if fast_input_type == \'traveler_check_purchase\':\n
  item_portal_type_list = (\'Check\',)\n
  disable_node = 1\n
\n
# retrieve reference field to filter list\n
reference = getattr(request, \'your_reference\', None)\n
if reference is None:\n
  reference = getattr(request, \'field_your_reference\', None)\n
\n
# filter by checkbook model\n
checkbook_model = getattr(request, \'your_checkbook_model\', None)\n
if checkbook_model is None:\n
  checkbook_model = getattr(request, \'field_your_checkbook_model\', None)\n
\n
# filter by title (check numbers)\n
title = getattr(request, \'your_title\', None)\n
if title is None:\n
  title = getattr(request, \'field_your_title\', None)\n
\n
nb = context.Delivery_getCheckbookList(\n
                    item_portal_type_list=item_portal_type_list,\n
                    disable_node=disable_node,\n
                    at_date=at_date,\n
                    node=node,\n
                    reference=reference,\n
                    title=title,\n
                    checkbook_model=checkbook_model,                    \n
                    count=True)\n
\n
return [[nb,],]\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>*args, **kw</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>ListBox_countCheckbook</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
