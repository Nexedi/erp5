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
            <value> <string>""" Retrieve the movement list of the transaction. """\n
movement_list = []\n
\n
sub = context.restrictedTraverse(context_document)\n
while sub.getParentValue().getPortalType() !=  "Synchronization Tool":\n
  sub = sub.getParentValue()\n
\n
im = sub.Base_getRelatedObjectList(portal_type=\'Integration Module\')[0].getObject()\n
#prod_module = im.getParentValue().product_module\n
#prod_pub = prod_module.getSourceSectionValue()\n
\n
# getter and corresponding property (the order is important)\n
getter_tuple_list = [\n
    (\'getTitle\', \'title\'),\n
    (\'getReference\', \'reference\'),\n
    (\'getSourceDebit\', \'debit_price\'),\n
    (\'getSourceCredit\', \'price\'),\n
]\n
\n
# browse the movement list, build the element to sort and movement\'s data\n
for movement in context.getMovementList():\n
  movement_dict = {\n
      \'title\': None,\n
      \'reference\': None,\n
      \'price\': None,\n
  }\n
  property_list = []\n
  # browse the main element of the movement\n
  for getter, key in getter_tuple_list:\n
    # XXX-Aurel : maybe there is better way to know if it is a cell\n
    if \'Cell\' in movement.getPortalType() and \\\n
        getter in [\'getTitle\', \'getReference\']:\n
      value = getattr(movement.getParentValue(), getter)()\n
    else:\n
      value = getattr(movement, getter)()\n
      if value is not None:\n
        if getter == \'getSourceDebit\':\n
          value = \'%.2f\' % value\n
        elif getter == \'getSourceCredit\':\n
          value = \'%.2f\' % value    \n
    if value is not None and value != 0:\n
      movement_dict[key] = value\n
      property_list.append(value)\n
\n
  if "price" in movement_dict.keys() and "debit_price" in movement_dict.keys():\n
    movement_dict["price"] = \'%.2f\' % (float(movement_dict["price"]) - float(movement_dict["debit_price"]))\n
  movement_list.append(movement_dict)\n
  # to not interfer with the sort, set to the end the object\n
  movement_dict[\'object\'] = movement\n
  context.log(movement_dict)\n
\n
#movement_list.sort()\n
return movement_list\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>context_document</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>PaymentTransaction_getLineList</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
