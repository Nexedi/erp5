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
            <value> <string>from zExceptions import Redirect\n
def error(msg):\n
  raise Redirect(\'%s/view?portal_status_message=%s\' % (\n
    context.absolute_url(),\n
    context.Base_translateString(msg))\n
  )\n
\n
node = context.getBaobabSource()\n
if node is None:\n
  error(\'Please select a source\')\n
if context.getPortalType() == \'Cash Movement New Not Emitted\' and \'transit\' not in node:\n
  error(\'Transit must be in source.\')\n
at_date = context.getStartDate()\n
if at_date is None:\n
  error(\'Please register a date.\')\n
\n
tracking_kw = {\n
  \'at_date\': at_date,\n
  \'node\': node,\n
  \'limit_expression\': (int(kw.get(\'list_start\', 0)), int(kw.get(\'list_lines\', 20))),\n
}\n
\n
request = context.REQUEST\n
reference = getattr(request, \'your_reference\', None)\n
if reference:\n
  tracking_kw[\'reference\'] = reference\n
\n
container_portal_type_set = {\n
  \'Monetary Reception\': None,\n
}\n
listbox = []\n
append = listbox.append\n
for o in context.portal_simulation.getCurrentTrackingList(**tracking_kw):\n
  cash_container = o.getObject()\n
  if cash_container.getParentValue().getPortalType() not in container_portal_type_set:\n
    continue\n
  container_line_list = cash_container.objectValues(portal_type=\'Container Line\')\n
  if len(container_line_list) == 0:\n
    # XXX: we should probably raise here instead\n
    continue\n
  container_line = container_line_list[0]\n
  append({\n
    \'uid\': cash_container.getUid(),\n
    \'reference\': cash_container.getReference(),\n
    \'cash_number_range_start\': cash_container.getCashNumberRangeStart(),\n
    \'cash_number_range_stop\': cash_container.getCashNumberRangeStop(),\n
    \'date\': o.date,\n
    \'resource_translated_title\': container_line.getResourceTranslatedTitle(),\n
    \'quantity\': container_line.getQuantity(),\n
    \'total_price\': container_line.getTotalPrice(fast=0),\n
  })\n
context.Base_updateDialogForm(listbox=listbox)\n
return context.ListBox_initializeFastInput()\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>*args, **kw</string> </value>
        </item>
        <item>
            <key> <string>_proxy_roles</string> </key>
            <value>
              <tuple>
                <string>Manager</string>
              </tuple>
            </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>ListBox_listCashContainers</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
