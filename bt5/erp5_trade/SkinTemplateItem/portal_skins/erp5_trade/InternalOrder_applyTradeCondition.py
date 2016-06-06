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

# This script searches for a trade condition matching the order\n
# and tries to complete some fields\n
\n
order = context\n
Base_translateString = context.Base_translateString\n
trade_condition_portal_type_list = (\'Internal Trade Condition\',)\n
\n
trade_condition_list = order.getSpecialiseValueList(\n
    portal_type=trade_condition_portal_type_list)\n
\n
tested_base_category_list = [ ]\n
for base_category in (\'source_section\', \'source\',\n
                      \'destination_section\', \'destination\', ):\n
  if context.getProperty(base_category):\n
    tested_base_category_list.append(base_category)\n
\n
count = len(tested_base_category_list) + 1\n
\n
# if no date is defined, use today\'s date to retrieve predicate that define start_date_range_min/max\n
if order.getStartDate() is None:\n
  predicate_context = order.asContext(start_date=DateTime())\n
else:\n
  predicate_context = order\n
\n
def rank_method(trade_condition):\n
  rank = 0\n
  destination_section_group = None\n
  destination_section = trade_condition.getDestinationSection()\n
  if destination_section:\n
    destination_section_group = trade_condition.getDestinationSectionValue().getGroup()\n
    if destination_section == context.getDestinationSection():\n
      rank += 10\n
    else:\n
      rank -= 2\n
  destination = trade_condition.getDestination()\n
  if destination:\n
    if destination == context.getDestination():\n
      rank += 10\n
    else:\n
      rank -= 2\n
  if trade_condition.getSourceSection():\n
    rank += 1\n
    if destination_section_group:\n
      source_section_group = trade_condition.getSourceSectionValue().getGroup()\n
      if source_section_group:\n
        if source_section_group.startswith(destination_section_group) \\\n
             or destination_section_group.startswith(source_section_group):\n
          # trade conditions where both sections are in the same group must have high priority\n
          rank += 20\n
  if trade_condition.getSource():\n
    rank += 1\n
  rank += len(trade_condition.getSpecialiseList())\n
  if trade_condition.getValidationState() == \'validated\':\n
    rank += 2\n
  return rank\n
\n
def sort_method(a, b):\n
  return -cmp(rank_method(a), rank_method(b))\n
\n
while count > 0 and len(trade_condition_list) == 0:\n
  count -= 1\n
  trade_condition_list = context.portal_domains.searchPredicateList(\n
      predicate_context, portal_type=trade_condition_portal_type_list,\n
      tested_base_category_list=tested_base_category_list[:count],\n
      sort_method=sort_method)\n
\n
if len(trade_condition_list ) == 0:\n
  message = Base_translateString(\'No trade condition.\')\n
else :\n
  # if more than one trade condition is found, simply apply the first one\n
  trade_condition=trade_condition_list[0].getObject()\n
\n
  order.Order_applyTradeCondition(trade_condition, force=force)\n
  # set date\n
  if hasattr(order, \'getReceivedDate\') and order.getReceivedDate() is None:\n
    context.setReceivedDate(DateTime())\n
\n
  message = Base_translateString(\'Order updated.\')\n
\n
if not batch_mode:\n
  return context.Base_redirect(form_id,\n
          keep_items=dict(portal_status_message=message))\n


]]></string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>form_id=\'view\', batch_mode=0, force=1</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>InternalOrder_applyTradeCondition</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
