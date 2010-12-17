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
            <value> <string>#print kw\n
#return printed\n
\n
task = context.task_module.newContent(\n
                                      portal_type=\'Task\',\n
                                      title=title,\n
                                      reference=reference,\n
                                      source=source,\n
                                      source_section=source_section,\n
                                      destination_decision=destination_decision,\n
                                      destination_section=destination_section,\n
                                      source_project=source_project,\n
                                      destination=destination,\n
                                      start_date=start_date,\n
                                      stop_date=stop_date,\n
                                      task_line_resource=task_line_resource,\n
                                      task_line_quantity=task_line_quantity,\n
                                      task_line_price=task_line_price,\n
                                      task_line_quantity_unit=task_line_quantity_unit,\n
                                      price_currency=price_currency,\n
                                      description=description,\n
                                     )\n
translateString = context.Base_translateString\n
portal_status_message = translateString("Object created.")\n
return task.Base_redirect(\'view\', \n
          keep_items = dict(portal_status_message=portal_status_message),)\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>title=None, reference=None, source=None, source_section=None, destination_decision=None, destination_section=None, source_project=None, destination=None, start_date=None, stop_date=None, task_line_resource=None, task_line_quantity=None, task_line_price=None, task_line_quantity_unit=None, price_currency=None, description=None, **kw</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>SaleOrderLine_createTask</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
