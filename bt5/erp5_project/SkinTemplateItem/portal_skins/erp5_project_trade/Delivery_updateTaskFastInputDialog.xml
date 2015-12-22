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

"""At first call, this script prefill values for all tasks that are\n
going to be created. If values are already there, this script check if\n
informations are correct.\n
"""\n
context.log(\'source_project_title\', source_project_title)\n
portal = context.getPortalObject()\n
line_portal_type = "Sale Order Line"\n
request = context.REQUEST\n
from string import zfill\n
from Products.ERP5Type.Document import newTempBase\n
from Products.ERP5Type.Message import translateString\n
\n
context.log(\'original listbox\', listbox)\n
initial_value_dict = {}\n
for line in (listbox or []):\n
  initial_value_dict[line[\'listbox_key\']] = line\n
\n
listbox = []\n
validation_errors = {}\n
def getRecursiveLineList(current, line_list):\n
  # We parse recursively all delivery line and we keep only ones\n
  # without childs\n
  sub_line_list = current.objectValues(portal_type=line_portal_type)\n
  if len(sub_line_list) == 0:\n
    if current.getPortalType() == line_portal_type:\n
      line_list.append(current)\n
  else:\n
    for sub_line in sub_line_list:\n
      getRecursiveLineList(sub_line, line_list)\n
line_list = []\n
getRecursiveLineList(context, line_list)\n
context.log("line_list", line_list)\n
i = 1\n
project_search_dict = {}\n
portal = context.getPortalObject()\n
for line in line_list:\n
  line_dict = {}\n
  line_id = "%s" % line.getUid()\n
  #line_dict[\'listbox_key\'] = "%s" % line_id\n
  key = zfill(i,3)\n
  for property_name in (\'title\', \'quantity_unit_title\', \'quantity\',\n
                        \'resource_title\', \'total_price\', \'price\',\n
                        \'reference\', \'relative_url\'):\n
    property_value = line.getProperty(property_name)\n
    line_dict[property_name] = line.getProperty(property_name)\n
    request.form["field_listbox_%s_new_%s"% (property_name, key)] = \\\n
      property_value\n
  line_dict.update(**initial_value_dict.get(key, {}))\n
  if line_dict.get(\'source_project_title\', \'\') == \'\':\n
    line_dict[\'source_project_title\'] = source_project_title\n
  line_source_project_title = line_dict.get(\'source_project_title\', \'\')\n
  request.form["field_listbox_%s_new_%s"% (\'source_project_title\', key)] = \\\n
      line_source_project_title\n
  if line_source_project_title != \'\':\n
    # Check if we have exactly one corresponding project\n
    result = project_search_dict.get(line_source_project_title, None)\n
    error_message = None\n
    if result is None:\n
      result = portal.portal_catalog(portal_type=(\'Project\', \'Project Line\'),\n
                                     title=line_source_project_title)\n
      project_search_dict[line_source_project_title] = result\n
    if len(result) == 0:\n
      error_message = "No such project"\n
    elif len(result) > 1:\n
      error_message = "Too many matching projects"\n
    else:\n
      line_dict[\'source_project_relative_url\'] = result[0].getRelativeUrl()\n
    if error_message:\n
      error = newTempBase(context, key)\n
      error.edit(error_text=error_message)\n
      validation_errors[\'listbox_source_project_title_new_%s\' % key] = error\n
  listbox.append(line_dict)\n
  i += 1\n
\n
context.log(\'listbox\', listbox)\n
context.Base_updateDialogForm(listbox=listbox,update=1,kw=kw)\n
\n
if len(validation_errors):\n
  request.set(\'field_errors\',validation_errors)\n
  kw[\'REQUEST\'] = request\n
\n
# if called from the validate action we create tasks\n
if create and len(validation_errors) == 0:\n
  for line in listbox:\n
    delivery_line = portal.restrictedTraverse(line[\'relative_url\'])\n
    task = portal.task_module.newContent(\n
              title=delivery_line.getTitle(),\n
              source_project=line[\'source_project_relative_url\'],\n
              source=delivery_line.getSourceTrade(),\n
              reference=delivery_line.getReference(),\n
              task_line_quantity=delivery_line.getQuantity(),\n
              task_line_price=delivery_line.getPrice(),\n
              task_line_quantity_unit=delivery_line.getQuantityUnit(),\n
              task_line_resource=delivery_line.getResource(),\n
              start_date=delivery_line.getStartDate(),\n
              stop_date=delivery_line.getStopDate(),\n
              description=delivery_line.getDescription(),\n
              price_currency=context.getPriceCurrency(),\n
              source_section=delivery_line.getSourceSection(),\n
              destination=delivery_line.getDestination(),\n
              causality=delivery_line.getRelativeUrl(),\n
              destination_section=delivery_line.getDestinationSection(),\n
              destination_decision=delivery_line.getDestinationDecision())\n
  return context.Base_redirect(form_id, keep_items=dict(\n
        portal_status_message=translateString(\'%s Tasks Created.\' %(len(listbox),))))\n
\n
return context.Delivery_viewTaskFastInputDialog(listbox=listbox, **kw)\n


]]></string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>listbox=None,source_project_title=\'\', create=0, form_id=None, **kw</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>Delivery_updateTaskFastInputDialog</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
