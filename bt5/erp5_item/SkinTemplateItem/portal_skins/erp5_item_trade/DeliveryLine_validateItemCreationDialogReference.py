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

dialog = getattr(context, dialog_id)\n
if dialog.has_field(\'your_item_extra_property_list\') and editor and len(request.get("field_listbox_reference_%s" % request.cell.uid))<=6:\n
  reference = "%s%s" % (request.get("field_your_prefix_reference"), request.get(\'field_listbox_reference_%s\' % request.cell.uid).zfill(6))  \n
  test_result = request.cell.Base_validateEan13Code(reference,request)\n
\n
  if test_result ==True:\n
    request.form["field_listbox_reference_%s" % request.cell.uid] = reference\n
    request.set("field_listbox_reference_%s" % request.cell.uid,reference)\n
    result = [x.getObject() for x in context.portal_catalog(portal_type = request.get("field_your_type"),\n
              reference= reference)]\n
    if (result !=[] or test_result ==False ):\n
      return False\n
  elif test_result == False:\n
    return False \n
return True\n


]]></string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>editor, request,dialog_id=\'DeliveryLine_viewItemCreationDialog\'</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>DeliveryLine_validateItemCreationDialogReference</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
