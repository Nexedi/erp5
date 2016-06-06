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
            <value> <string>"""Jump to the order(s) this invoice was created from.\n
"""\n
portal = context.getPortalObject()\n
translateString = portal.Base_translateString\n
packing_list_list = context.getCausalityValueList(portal_type=packing_list_type,\n
                                                  checked_permission=\'View\')\n
related_order_uid_list = []\n
if packing_list_list:\n
  if len(packing_list_list) == 1:\n
    related_order_list = packing_list_list[0].getCausalityValueList(\n
                                portal_type=order_type,\n
                                checked_permission=\'View\')\n
    related_order_uid_list = [o.getUid() for o in related_order_list]\n
    if len(related_order_list) == 1:\n
      related_object = related_order_list[0]\n
      message = translateString(\n
      # first, try to get a full translated message with portal types\n
      "%s related to %s." % (related_object.getPortalType(), context.getPortalType()),\n
       # if not found, fallback to generic translation\n
      default = unicode(translateString(\'${this_portal_type} related to ${that_portal_type} : ${that_title}.\',\n
        mapping={"this_portal_type" : related_object.getTranslatedPortalType(),\n
                 "that_portal_type" : context.getTranslatedPortalType(),\n
                 "that_title" : context.getTitleOrId() }), \'utf8\'))\n
      return related_order_list[0].Base_redirect(\'view\',\n
                              keep_items=dict(portal_status_message=message))\n
  else:\n
    for packing_list in packing_list_list:\n
      related_order_uid_list.extend(\n
        [x.getUid() for x in packing_list.getCausalityValueList(\n
                                          portal_type=order_type,\n
                                          checked_permission=\'View\')])\n
\n
if related_order_uid_list:\n
  order_module = portal.getDefaultModule(order_type)\n
  return order_module.Base_redirect(\'view\',\n
              keep_items=dict(reset=1,\n
                              uid=related_order_uid_list))\n
\n
return context.Base_redirect(form_id,\n
              keep_items=dict(portal_status_message=\n
                                translateString(\'No ${portal_type} related.\',\n
                                       mapping=dict(portal_type=translateString(order_type)))))\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>packing_list_type, order_type, form_id=\'view\'</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>Invoice_jumpToOrder</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
