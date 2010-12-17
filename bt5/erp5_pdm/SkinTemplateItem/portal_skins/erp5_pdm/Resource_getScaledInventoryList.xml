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

"""Returns inventory list for resource scaled for chart\n
\n
Needs from_date and at_date to know time size.\n
\n
Uses sampling_amount, defaults to 20.\n
\n
Samples inventory by proper differency, returns\n
sampling_amount inventory lines, sorted by date.\n
"""\n
\n
# XXX: Might be set in preferences\n
sampling_amount = kwargs.get(\'sampling_amount\',20)\n
\n
from Products.ERP5Type.Document import newTempDocument\n
from DateTime import DateTime\n
\n
resource = context\n
request = context.REQUEST\n
portal = context.getPortalObject()\n
\n
node = portal.restrictedTraverse(kwargs.get(\'node\'))\n
from_date = kwargs.get(\'from_date\')\n
at_date = kwargs.get(\'at_date\')\n
variation_list = kwargs.get(\'variation_list\')\n
variation_text = \'\'\n
\n
if variation_list is not None and len(variation_list) > 0:\n
  # imitate behaviour from VariatedMixin.getVariationText\n
  # to create text\n
  variation_list.sort()\n
  variation_text = \'\\n\'.join(variation_list)\n
\n
if from_date is None or at_date is None or node is None:\n
  return []\n
 \n
# Lower by one, to be include from_date and at_date\n
sampling_delta = ( DateTime(at_date) - DateTime(from_date) ) / (sampling_amount - 1)\n
\n
common_kw = {}\n
common_kw.update(\n
  node_uid = node.getUid(),\n
  sort_on = ((\'stock.date\',\'desc\'),),\n
  variation_text = variation_text,\n
)\n
\n
inventory_tuple_list = []\n
\n
precise_time_format = \'%Y/%m/%d %H:%M.%S\'\n
base_time_format = precise_time_format\n
rough_time_form = \'%Y/%m/%d\'\n
# XXX: Below performance issues:\n
#  * sampling made in dumb way - it shall use SQL\n
#  * inventory is invoked 3 times for each sample\n
for i in range(0,sampling_amount):\n
  this_date = DateTime(from_date + sampling_delta * i)\n
  formatted_date = this_date.strftime(base_time_format)\n
  internal_tuple = (\n
    formatted_date,\n
    resource.getCurrentInventory(\n
      at_date = this_date,\n
      **common_kw\n
    ),\n
    resource.getAvailableInventory(\n
      at_date = this_date,\n
      **common_kw\n
    ),\n
    resource.getFutureInventory(\n
      at_date = this_date,\n
      **common_kw\n
    ),\n
  )\n
  inventory_tuple_list.append(internal_tuple)\n
\n
return_list = [] \n
for a in range(0,len(inventory_tuple_list)):\n
  d = newTempDocument( portal, str(a) )\n
  data = inventory_tuple_list[a]\n
  d.edit(\n
    title = \'title %s\'%(a,),\n
    date = data[0],\n
    current = data[1],\n
    available = data[2],\n
    future = data[3],\n
  )\n
  return_list.append(d)\n
return return_list\n


]]></string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>*args, **kwargs</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>Resource_getScaledInventoryList</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
